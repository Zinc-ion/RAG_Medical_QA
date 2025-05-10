import os
import logging


from lightragPkg import LightRAG, QueryParam
from lightragPkg.llm.zhipu import zhipu_complete
from lightragPkg.llm.ollama import ollama
from lightragPkg.utils import EmbeddingFunc

WORKING_DIR = "../../dickens"

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
    llm_model_max_token_size=32768,
    embedding_func=EmbeddingFunc(
        embedding_dim=2048,  # Zhipu embedding-3 dimension
        max_token_size=8192,
        func=lambda texts: zhipu_embedding(texts),
    ),
)

with open("C://Users//PC//Desktop//learn_pytorch//LightRAG_QA_Sys//LightRAG//doc//medical-books//内科疾病鉴别诊断学//content//chap01.txt", "r", encoding="utf-8") as f:
    rag.insert(f.read())

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
    rag.query("文章的主要讲了些什么?", param=QueryParam(mode="hybrid"))
)
