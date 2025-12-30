import os
import sys
import logging
import argparse
import time
from datetime import datetime
from unittest.mock import patch

# Add LightRAG directory to sys.path so lightragPkg can be imported as a top-level package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'LightRAG')))

from lightragPkg.lightrag import LightRAG, QueryParam
from lightragPkg.llm.zhipu import zhipu_complete
from lightragPkg.llm.ollama import ollama_embedding
from lightragPkg.utils import EmbeddingFunc

# Set up argument parser
parser = argparse.ArgumentParser(description='Insert news into LightRAG')
parser.add_argument('--thinking', action='store_true', help='Enable deep thinking (GLM-4.7)')
args = parser.parse_args()

WORKING_DIR = "./dickens"  #存放数据的目录

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

api_key = os.environ.get("ZHIPUAI_API_KEY")
if api_key is None:
    raise Exception("Please set ZHIPU_API_KEY in your environment")

# Configure LLM kwargs based on thinking argument
llm_kwargs = {}
if args.thinking:
    llm_kwargs["thinking"] = {"type": "enabled"}

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=zhipu_complete,
    llm_model_name="glm-4.7",  # Using the most cost/performance balance model, but you can change it here.
    llm_model_max_async=4,
    chunk_token_size=256,
    llm_model_max_token_size=32768,
    llm_model_kwargs=llm_kwargs,
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




text09="""
2009年12月23日
世界卫生组织12月23日表示，目前在北半球温带地区，甲型H1N1流感病毒的传播仍然活跃而广泛，部分地区的病毒活动仍在增加，不过总体而言，发病的高峰时期似乎已经过去。
美国和加拿大的流感病毒活动在地域上仍具有广泛性，但由于流感样疾病而入院治疗或死亡的病例数自六周前达到顶峰后一直稳步减少，在加拿大已低于季节基准线。

在东亚，流感病毒活动仍然活跃但总体呈减弱趋势。日本、中国、蒙古的流感样疾病暴发高峰期已经过去。

不过，在中东欧、西亚、中亚和南亚部分地区，流感病毒的活动仍在继续增加。

截止到12月20日，全世界200多个国家和地区都发现了经检测确认的甲型H1N1流感病例，至少1万1516名患者死亡。
"""

text23 = """
2023世界流感日：我国将进入流感高发期 专家提醒做好防控
来源：新华网 | 2023年11月01日 13:49:34
原标题：2023世界流感日：我国将进入流感高发期 专家提醒做好防控
新华社北京11月1日电 题：2023世界流感日：我国将进入流感高发期 专家提醒做好防控
新华社记者顾天成
11月1日是世界流感日。进入11月，秋冬季气温变化幅度较大，也是流感等各类呼吸道传染病的高发期。当前我国流感整体流行情况如何？为何要及时接种流感疫苗，接种前后要注意什么？国家疾控局邀请专家接受媒体采访，解答公众关心的流感防控相关热点问题。
“目前我国流感活动处于中低水平但呈上升趋势。”中国疾控中心病毒病预防控制所国家流感中心主任王大燕介绍，在我国南方省份，9月以来出现甲型H3N2亚型为主导的流感活动升高，与乙型Victoria系流感病毒共同流行。而在北方个别省份，10月以来开始出现流感活动升高，以甲型H3N2亚型为主。
王大燕表示，预计我国南方省份、北方省份会逐渐进入流感高发期，并出现秋冬季的流感流行高峰，将呈季节性流行。在此期间，流感聚集性疫情可能会增多，聚集性疫情主要发生在学校、幼托机构、养老机构等人群密集的场所，要注意提前做好防控准备。
"""

text25_01 = """
2025年12月5日 健康及卫生
世界卫生组织周五通报，美国自2024年初以来确诊第71例人类感染甲型禽流感病例，其中11月15日报告的病例经美国疾病控制与预防中心实验室测序确认感染H5N5流感病毒。这是全球首例由H5N5禽流感病毒引发的人类感染病例。

H5N5流感病毒是一种甲型禽流感病毒，主要感染家禽和野鸟，是禽流感的典型病毒来源。人类感染极为罕见，多发生在直接接触受感染禽类或其分泌物的情况下，目前尚无证据显示该病毒可在人际间持续传播。该病毒属于高度致病性禽流感病毒，能够引起禽类严重疾病和高死亡率。世卫组织评估，公众总体感染风险低，但从事禽类养殖、屠宰或防疫工作的人员职业暴露风险为低至中等水平。为防控病毒扩散，建议采取禽类隔离、扑杀感染禽类、佩戴个人防护装备，并对接触者进行追踪和检测，同时加强全球监测与病毒信息共享。

世卫组织表示，美国卫生部门正持续开展流行病学调查，并追踪接触者，目前未发现其他病例。鉴于流感病毒持续变异，世卫组织再次强调全球监测的重要性，以便及时发现可能影响人类健康的新兴或流行流感病毒，并共享病毒学、流行病学及临床信息进行风险评估。
"""

text25_02 = """
2025年12月16日 健康及卫生
世界卫生组织本周二指出，随着北半球流感季节提前到来，一种新型流感病毒变种正在快速传播，但接种疫苗依然是最有效的防护手段。

世卫组织流行病与大流行病管理部门全球呼吸道威胁项目负责人张文清在日内瓦向记者表示，当前流感与其他呼吸道病毒正处于激增态势，今年疫情的特点表现为“AH3N2亚型流感病毒的出现与迅速扩散”。

她介绍，这种名为J.2.4.1（亦称“K 型”）的变异株于今年8月首次在澳大利亚和新西兰发现，目前已在超过30个国家监测到其传播。

现有疫苗仍具防护效力
张文清指出，尽管病毒发生显著基因进化，但目前的流行病学数据并未显示疾病严重程度有所加剧。她解释称，流感病毒持续演变，这正是流感疫苗成分需要定期更新的原因。

她表示，世卫组织通过其长期运行的全球流感监测与应对系统，与国际专家协同追踪病毒变异，评估公共卫生风险，并每年两次更新疫苗成分建议。

她指出，该新变种虽未被纳入本季北半球流感疫苗组分，但早期证据表明，现有季节性疫苗仍能有效预防重症并降低住院风险。

据世卫组织估算，全球每年约有10亿季节性流感病例，其中重症呼吸道感染可达500万例，每年因流感相关呼吸道疾病死亡人数约65万。
"""


# Mocking the system time for each insert to simulate different ingestion times


# with patch("lightragPkg.lightrag.datetime") as mock_datetime, \
#      patch("lightragPkg.kg.nano_vector_db_impl.time") as mock_time:
#     target_date = datetime(2009, 12, 23)
#     mock_datetime.now.return_value = target_date
#     mock_time.time.return_value = target_date.timestamp()
#     rag.insert(text09)

with patch("lightragPkg.lightrag.datetime") as mock_datetime, \
     patch("lightragPkg.kg.nano_vector_db_impl.time") as mock_time:
    target_date = datetime(2025, 12, 5)
    mock_datetime.now.return_value = target_date
    mock_time.time.return_value = target_date.timestamp()
    rag.insert(text25_01)

# with patch("lightragPkg.lightrag.datetime") as mock_datetime, \
#      patch("lightragPkg.kg.nano_vector_db_impl.time") as mock_time:
#     target_date = datetime(2023, 11, 1)
#     mock_datetime.now.return_value = target_date
#     mock_time.time.return_value = target_date.timestamp()
#     rag.insert(text23)


# with patch("lightragPkg.lightrag.datetime") as mock_datetime, \
#      patch("lightragPkg.kg.nano_vector_db_impl.time") as mock_time:
#     target_date = datetime(2025, 12, 16)
#     mock_datetime.now.return_value = target_date
#     mock_time.time.return_value = target_date.timestamp()
#     rag.insert(text25)
