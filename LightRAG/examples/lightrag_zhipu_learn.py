import os
import logging


from lightrag.lightrag import LightRAG, QueryParam
from lightrag.llm.zhipu import zhipu_complete
from lightrag.llm.ollama import ollama_embedding
from lightrag.utils import EmbeddingFunc

WORKING_DIR = "../dickens"  #存放数据的目录

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

api_key = os.environ.get("ZHIPUAI_API_KEY")
if api_key is None:
    raise Exception("Please set ZHIPU_API_KEY in your environment")


rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=zhipu_complete,
    llm_model_name="glm-4-flashx",  # Using the most cost/performance balance model, but you can change it here.
    llm_model_max_async=4,
    chunk_token_size=512,
    llm_model_max_token_size=32768,
    embedding_func=EmbeddingFunc(
        embedding_dim=1024,  # 注意一定要和模型的embedding_dim一致！！
        max_token_size=8192,
        func=lambda texts: ollama_embedding(  # 使用ollama中的模型
            texts,
            embed_model="quentinz/bge-large-zh-v1.5",
            host="http://localhost:11434",
                                            )
    ),
)

# with open("D://learn_pytorch//LightRAG_QA_Sys//LightRAG//doc//medical-books//ICU主治医师手册//content//chap25.txt", "r", encoding="utf-8") as f:
#     rag.insert(f.read())

# 循环插入所有章节
# for i in range(1, 26):
#     print(f"D://learn_pytorch//LightRAG_QA_Sys//LightRAG//doc//medical-books//ICU主治医师手册//content//chap{i:02d}.txt")
#     print(f"ICU主治医师手册//content//chap{i:02d}")
#     with open(f"D://learn_pytorch//LightRAG_QA_Sys//LightRAG//doc//medical-books//ICU主治医师手册//content//chap{i:02d}.txt", "r",
#               encoding="utf-8") as f:
#         rag.insert(f.read())
# 4.29抽取完24章，还剩最后ICU主治的25章没抽


# # Perform naive search
# print(
#     rag.query("What are the top themes in this story?", param=QueryParam(mode="naive"))
# )
#
# # Perform local search
# print(
#     rag.query("What are the top themes in this story?", param=QueryParam(mode="local"))
# )
#
# # Perform global search
# print(
#     rag.query("What are the top themes in this story?", param=QueryParam(mode="global"))
# )

# Perform hybrid search
print(
    rag.query("文章主要内容是什么?", param=QueryParam(mode="hybrid"))
)
