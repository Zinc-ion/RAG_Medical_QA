import asyncio
import os
import json
import base64
from typing import Any, final
from dataclasses import dataclass
import numpy as np

import time

from lightragPkg.utils import (
    logger,
    compute_mdhash_id,
    write_json,
)
import pipmaster as pm
from lightragPkg.base import (
    BaseVectorStorage,
)

if not pm.is_installed("nano-vectordb"):
    pm.install("nano-vectordb")

from nano_vectordb import NanoVectorDB


@final
@dataclass
class NanoVectorDBStorage(BaseVectorStorage):
    def __post_init__(self):
        # Initialize lock only for file operations
        self._save_lock = asyncio.Lock()
        # Use global config value if specified, otherwise use default
        kwargs = self.global_config.get("vector_db_storage_cls_kwargs", {})
        cosine_threshold = kwargs.get("cosine_better_than_threshold")
        if cosine_threshold is None:
            raise ValueError(
                "cosine_better_than_threshold must be specified in vector_db_storage_cls_kwargs"
            )
        self.cosine_better_than_threshold = cosine_threshold

        self._client_file_name = os.path.join(
            self.global_config["working_dir"], f"vdb_{self.namespace}.json"
        )

        # --- Fix for loading compatibility ---
        if os.path.exists(self._client_file_name):
            try:
                with open(self._client_file_name, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if 'matrix' is a list (our custom save format)
                if isinstance(data.get("matrix"), list):
                    logger.info(f"Detected list format in {self._client_file_name}, converting to Base64 for NanoVectorDB compatibility...")
                    
                    # Convert list back to numpy array
                    matrix_array = np.array(data["matrix"], dtype=np.float32)
                    
                    # Convert to bytes then Base64 string
                    matrix_bytes = matrix_array.tobytes()
                    matrix_base64 = base64.b64encode(matrix_bytes).decode('ascii')
                    
                    # Update data
                    data["matrix"] = matrix_base64
                    
                    # Save back to file in the format NanoVectorDB expects
                    with open(self._client_file_name, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False)
                    
                    logger.info(f"Successfully converted {self._client_file_name} to NanoVectorDB compatible format.")
            except Exception as e:
                logger.error(f"Error checking/converting VDB file format: {e}")
        # -------------------------------------

        self._max_batch_size = self.global_config["embedding_batch_num"]
        self._client = NanoVectorDB(
            self.embedding_func.embedding_dim, storage_file=self._client_file_name
        )

    async def upsert(self, data: dict[str, dict[str, Any]]) -> None:
        logger.info(f"Inserting {len(data)} to {self.namespace}")
        if not data:
            return

        current_time = time.time()
        list_data = [
            {
                "__id__": k,
                "__created_at__": current_time,
                **{k1: v1 for k1, v1 in v.items() if k1 in self.meta_fields},
            }
            for k, v in data.items()
        ]
        contents = [v["content"] for v in data.values()]
        batches = [
            contents[i : i + self._max_batch_size]
            for i in range(0, len(contents), self._max_batch_size)
        ]

        embedding_tasks = [self.embedding_func(batch) for batch in batches]
        embeddings_list = await asyncio.gather(*embedding_tasks)

        embeddings = np.concatenate(embeddings_list)
        if len(embeddings) == len(list_data):
            for i, d in enumerate(list_data):
                d["__vector__"] = embeddings[i]
            results = self._client.upsert(datas=list_data)
            return results
        else:
            # sometimes the embedding is not returned correctly. just log it.
            logger.error(
                f"embedding is not 1-1 with data, {len(embeddings)} != {len(list_data)}"
            )

    async def query(self, query: str, top_k: int) -> list[dict[str, Any]]:
        embedding = await self.embedding_func([query])
        embedding = embedding[0]
        results = self._client.query(
            query=embedding,
            top_k=top_k,
            better_than_threshold=self.cosine_better_than_threshold,
        )
        results = [
            {
                **dp,
                "id": dp["__id__"],
                "distance": dp["__metrics__"],
                "created_at": dp.get("__created_at__"),
            }
            for dp in results
        ]
        return results

    @property
    def client_storage(self):
        return getattr(self._client, "_NanoVectorDB__storage")

    async def delete(self, ids: list[str]):
        """Delete vectors with specified IDs

        Args:
            ids: List of vector IDs to be deleted
        """
        try:
            self._client.delete(ids)
            logger.info(
                f"Successfully deleted {len(ids)} vectors from {self.namespace}"
            )
        except Exception as e:
            logger.error(f"Error while deleting vectors from {self.namespace}: {e}")

    async def delete_entity(self, entity_name: str) -> None:
        try:
            entity_id = compute_mdhash_id(entity_name, prefix="ent-")
            logger.debug(
                f"Attempting to delete entity {entity_name} with ID {entity_id}"
            )
            # Check if the entity exists
            if self._client.get([entity_id]):
                await self.delete([entity_id])
                logger.debug(f"Successfully deleted entity {entity_name}")
            else:
                logger.debug(f"Entity {entity_name} not found in storage")
        except Exception as e:
            logger.error(f"Error deleting entity {entity_name}: {e}")

    async def delete_entity_relation(self, entity_name: str) -> None:
        try:
            relations = [
                dp
                for dp in self.client_storage["data"]
                if dp["src_id"] == entity_name or dp["tgt_id"] == entity_name
            ]
            logger.debug(f"Found {len(relations)} relations for entity {entity_name}")
            ids_to_delete = [relation["__id__"] for relation in relations]

            if ids_to_delete:
                await self.delete(ids_to_delete)
                logger.debug(
                    f"Deleted {len(ids_to_delete)} relations for {entity_name}"
                )
            else:
                logger.debug(f"No relations found for entity {entity_name}")
        except Exception as e:
            logger.error(f"Error deleting relations for {entity_name}: {e}")

    async def index_done_callback(self) -> None:
        async with self._save_lock:
            logger.info(f"Saving NanoVectorDB to {self._client_file_name}")
            try:
                self._client.save()
                logger.info(f"Saved NanoVectorDB to {self._client_file_name} using client.save()")
            except Exception as e:
                logger.error(f"Failed to save NanoVectorDB using client.save(): {e}")
            
            # Force save using json.dump with custom encoder to ensure persistence
            try:
                # Prepare data for NanoVectorDB format (matrix as Base64)
                # We access the internal storage dict directly
                storage_data = self.client_storage
                
                # Create a copy to avoid modifying the in-memory object used by client
                save_data = storage_data.copy()
                
                # If matrix is a numpy array, convert to Base64
                if isinstance(save_data.get("matrix"), np.ndarray):
                     matrix_bytes = save_data["matrix"].tobytes()
                     save_data["matrix"] = base64.b64encode(matrix_bytes).decode('ascii')
                # If matrix is a list (fallback), convert to numpy then Base64
                elif isinstance(save_data.get("matrix"), list):
                     matrix_array = np.array(save_data["matrix"], dtype=np.float32)
                     matrix_bytes = matrix_array.tobytes()
                     save_data["matrix"] = base64.b64encode(matrix_bytes).decode('ascii')
                
                with open(self._client_file_name, "w", encoding="utf-8") as f:
                    json.dump(save_data, f, indent=4, ensure_ascii=False)
                    
                logger.info(f"Saved NanoVectorDB to {self._client_file_name} using custom json dump (Base64 format)")
            except Exception as e:
                logger.error(f"Failed to save NanoVectorDB using custom json dump: {e}")
