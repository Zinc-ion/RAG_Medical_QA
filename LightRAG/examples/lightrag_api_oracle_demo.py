from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi import Query
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, Any

import sys
import os


from pathlib import Path

import asyncio
import nest_asyncio
from lightragPkg import LightRAG, QueryParam
from lightragPkg.llm.openai import openai_complete_if_cache, openai_embed
from lightragPkg.utils import EmbeddingFunc
import numpy as np


print(os.getcwd())
script_directory = Path(__file__).resolve().parent.parent
sys.path.append(os.path.abspath(script_directory))


# Apply nest_asyncio to solve event loop issues
nest_asyncio.apply()

DEFAULT_RAG_DIR = "index_default"


# We use OpenAI compatible API to call LLM on Oracle Cloud
# More docs here https://github.com/jin38324/OCI_GenAI_access_gateway
BASE_URL = "http://xxx.xxx.xxx.xxx:8088/v1/"
APIKEY = "ocigenerativeai"

# Configure working directory
WORKING_DIR = os.environ.get("RAG_DIR", f"{DEFAULT_RAG_DIR}")
print(f"WORKING_DIR: {WORKING_DIR}")
LLM_MODEL = os.environ.get("LLM_MODEL", "cohere.command-r-plus-08-2024")
print(f"LLM_MODEL: {LLM_MODEL}")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "cohere.embed-multilingual-v3.0")
print(f"EMBEDDING_MODEL: {EMBEDDING_MODEL}")
EMBEDDING_MAX_TOKEN_SIZE = int(os.environ.get("EMBEDDING_MAX_TOKEN_SIZE", 512))
print(f"EMBEDDING_MAX_TOKEN_SIZE: {EMBEDDING_MAX_TOKEN_SIZE}")

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

os.environ["ORACLE_USER"] = ""
os.environ["ORACLE_PASSWORD"] = ""
os.environ["ORACLE_DSN"] = ""
os.environ["ORACLE_CONFIG_DIR"] = "path_to_config_dir"
os.environ["ORACLE_WALLET_LOCATION"] = "path_to_wallet_location"
os.environ["ORACLE_WALLET_PASSWORD"] = "wallet_password"
os.environ["ORACLE_WORKSPACE"] = "company"


async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    return await openai_complete_if_cache(
        LLM_MODEL,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=APIKEY,
        base_url=BASE_URL,
        **kwargs,
    )


async def embedding_func(texts: list[str]) -> np.ndarray:
    return await openai_embed(
        texts,
        model=EMBEDDING_MODEL,
        api_key=APIKEY,
        base_url=BASE_URL,
    )


async def get_embedding_dim():
    test_text = ["This is a test sentence."]
    embedding = await embedding_func(test_text)
    embedding_dim = embedding.shape[1]
    return embedding_dim


async def init():
    # Detect embedding dimension
    embedding_dimension = await get_embedding_dim()
    print(f"Detected embedding dimension: {embedding_dimension}")
    # Create Oracle DB connection
    # The `config` parameter is the connection configuration of Oracle DB
    # More docs here https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html
    # We storage data in unified tables, so we need to set a `workspace` parameter to specify which docs we want to store and query
    # Below is an example of how to connect to Oracle Autonomous Database on Oracle Cloud

    # Initialize LightRAG
    # We use Oracle DB as the KV/vector/graph storage
    rag = LightRAG(
        enable_llm_cache=False,
        working_dir=WORKING_DIR,
        chunk_token_size=512,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=embedding_dimension,
            max_token_size=512,
            func=embedding_func,
        ),
        graph_storage="OracleGraphStorage",
        kv_storage="OracleKVStorage",
        vector_storage="OracleVectorDBStorage",
    )

    return rag


# Extract and Insert into LightRAG storage
# with open("./dickens/book.txt", "r", encoding="utf-8") as f:
#   await rag.ainsert(f.read())

# # Perform search in different modes
# modes = ["naive", "local", "global", "hybrid"]
# for mode in modes:
#     print("="*20, mode, "="*20)
#     print(await rag.aquery("这篇文档是关于什么内容的?", param=QueryParam(mode=mode)))
#     print("-"*100, "\n")

# Data models


class QueryRequest(BaseModel):
    query: str
    mode: str = "hybrid"
    only_need_context: bool = False
    only_need_prompt: bool = False


class DataRequest(BaseModel):
    limit: int = 100


class InsertRequest(BaseModel):
    text: str


class Response(BaseModel):
    status: str
    data: Optional[Any] = None
    message: Optional[str] = None


# API routes

rag = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag
    rag = await init()
    print("done!")
    yield


app = FastAPI(
    title="LightRAG API", description="API for RAG operations", lifespan=lifespan
)


@app.post("/query", response_model=Response)
async def query_endpoint(request: QueryRequest):
    # try:
    # loop = asyncio.get_event_loop()
    if request.mode == "naive":
        top_k = 3
    else:
        top_k = 60
    result = await rag.aquery(
        request.query,
        param=QueryParam(
            mode=request.mode,
            only_need_context=request.only_need_context,
            only_need_prompt=request.only_need_prompt,
            top_k=top_k,
        ),
    )
    return Response(status="success", data=result)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


@app.get("/data", response_model=Response)
async def query_all_nodes(type: str = Query("nodes"), limit: int = Query(100)):
    if type == "nodes":
        result = await rag.chunk_entity_relation_graph.get_all_nodes(limit=limit)
    elif type == "edges":
        result = await rag.chunk_entity_relation_graph.get_all_edges(limit=limit)
    elif type == "statistics":
        result = await rag.chunk_entity_relation_graph.get_statistics()
    return Response(status="success", data=result)


@app.post("/insert", response_model=Response)
async def insert_endpoint(request: InsertRequest):
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: rag.insert(request.text))
        return Response(status="success", message="Text inserted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/insert_file", response_model=Response)
async def insert_file(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        # Read file content
        try:
            content = file_content.decode("utf-8")
        except UnicodeDecodeError:
            # If UTF-8 decoding fails, try other encodings
            content = file_content.decode("gbk")
        # Insert file content
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: rag.insert(content))

        return Response(
            status="success",
            message=f"File content from {file.filename} inserted successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8020)

# Usage example
# To run the server, use the following command in your terminal:
# python lightrag_api_openai_compatible_demo.py

# Example requests:
# 1. Query:
# curl -X POST "http://127.0.0.1:8020/query" -H "Content-Type: application/json" -d '{"query": "your query here", "mode": "hybrid"}'

# 2. Insert text:
# curl -X POST "http://127.0.0.1:8020/insert" -H "Content-Type: application/json" -d '{"text": "your text here"}'

# 3. Insert file:
# curl -X POST "http://127.0.0.1:8020/insert_file" -H "Content-Type: multipart/form-data" -F "file=@path/to/your/file.txt"


# 4. Health check:
# curl -X GET "http://127.0.0.1:8020/health"
