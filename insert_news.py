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

text20 = """
2020年12月22日 健康及卫生
世界卫生组织21日就英国近期发现的变异新冠病毒发布首份详细信息，表示目前没有理由认定变异病毒比现有病毒更加凶险，也没有证据显示其将使现有的疫苗或治疗方法失效，但仍需开展更多研究调查。该组织同时建议各国检查目前使用的荧光定量检测（即PCR检测）是否会受到影响，建议平行使用针对不同基因的多项检测以保障有效性。

变异病毒
世卫组织表示，该组织于今年12月14日接到英国政府通报，称该国境内发现一种变异的新型冠状病毒，根据发现时间将其命名为SARS-CoV-2 VUI 202012/01，意为正在接受调查的、2020年12月第一号变异新冠病毒。

世卫组织表示，12月初，英格兰东南部的新冠患者数量突然激增，在14天内增加了三倍以上，此后所开展的流行病学和病毒学调查发现了这种变异病毒。现有研究认为，今年9月20日在英格兰东南部的肯特郡出现了首例受到该变异病毒感染的病例，10月5日至12月13日期间，在对英格兰东南部确诊患者所进行的常规病毒基因测序中，发现此种变异病毒的概率达到50%以上，大多数感染者的年龄都在60岁以下。

世卫组织表示，该变异病毒中包含14个氨基酸突变和3个蛋白质构件缺失，部分变异可能影响其在人群中的传播能力。其中一种被命名为N501Y的变异在英国和南非分别出现，但两者之间并无关联。

在英国所开展的初步研究显示，该变异病毒的传播能力较此前提升了40-70%，除英国外，澳大利亚、丹麦、意大利、冰岛与荷兰等国也已报告发现了这种变异病毒。

世卫组织表示，有关此种变异病毒生物学特性，及其对临床症状严重程度、抗体反应和疫苗有效性的研究目前正在开展，仍需等待研究结果和进一步的信息。

公共卫生应对措施
世卫组织表示，英国政府已将该变异病毒的基因数据上传至“全球共享所有流感数据行动数据库”（GISAID），同时正密切监测国内情况，并开展进一步的流行病学和病毒学调查。

英国政府同时于12月19日将该国受影响地区的防控级别上调至最高的四级，相关措施包括减少社交聚会、严格出行限制、要求尽可能居家办公，以及关闭非必要商户等。
"""

text25 = """
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


with patch("lightragPkg.lightrag.datetime") as mock_datetime, \
     patch("lightragPkg.kg.nano_vector_db_impl.time") as mock_time:
    target_date = datetime(2009, 12, 23)
    mock_datetime.now.return_value = target_date
    mock_time.time.return_value = target_date.timestamp()
    rag.insert(text09)

# with patch("lightragPkg.lightrag.datetime") as mock_datetime, \
#      patch("lightragPkg.kg.nano_vector_db_impl.time") as mock_time:
#     target_date = datetime(2020, 12, 22)
#     mock_datetime.now.return_value = target_date
#     mock_time.time.return_value = target_date.timestamp()
#     rag.insert(text20)

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
