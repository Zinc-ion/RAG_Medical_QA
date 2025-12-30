import streamlit as st
import ollama
import py2neo
import random
import re
import os
import sys
import json
import datetime
import logging
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

#lightragPkg
from LightRAG.lightragPkg.lightrag import LightRAG, QueryParam
from LightRAG.lightragPkg.llm.zhipu import zhipu_complete
from LightRAG.lightragPkg.llm.ollama import ollama_embedding
from LightRAG.lightragPkg.utils import EmbeddingFunc

# 加载环境变量
from dotenv import load_dotenv

# 添加LightRAG目录到系统路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'LightRAG'))

# 加载.env文件
load_dotenv()

WORKING_DIR = "./dickens"  #存放数据的目录

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

# --- 模拟动态新闻数据流 ---
FAKE_NEWS_DATA = [
    """2025年12月16日 健康及卫生
世界卫生组织本周二指出，随着北半球流感季节提前到来，一种新型流感病毒变种正在快速传播，但接种疫苗依然是最有效的防护手段。

世卫组织流行病与大流行病管理部门全球呼吸道威胁项目负责人张文清在日内瓦向记者表示，当前流感与其他呼吸道病毒正处于激增态势，今年疫情的特点表现为“AH3N2亚型流感病毒的出现与迅速扩散”。

她介绍，这种名为J.2.4.1（亦称“K 型”）的变异株于今年8月首次在澳大利亚和新西兰发现，目前已在超过30个国家监测到其传播。

现有疫苗仍具防护效力
张文清指出，尽管病毒发生显著基因进化，但目前的流行病学数据并未显示疾病严重程度有所加剧。她解释称，流感病毒持续演变，这正是流感疫苗成分需要定期更新的原因。

她表示，世卫组织通过其长期运行的全球流感监测与应对系统，与国际专家协同追踪病毒变异，评估公共卫生风险，并每年两次更新疫苗成分建议。

她指出，该新变种虽未被纳入本季北半球流感疫苗组分，但早期证据表明，现有季节性疫苗仍能有效预防重症并降低住院风险。

据世卫组织估算，全球每年约有10亿季节性流感病例，其中重症呼吸道感染可达500万例，每年因流感相关呼吸道疾病死亡人数约65万。""",
    
    """【2024-12-30 医疗科技进展】
    Z大学附属医院神经内科团队宣布，“经颅磁刺激（TMS）”在治疗慢性偏头痛方面取得突破。
    研究表明：每周进行3次TMS治疗，配合口服微量褪黑素，可使发作频率降低70%。
    禁忌症：体内植入心脏起搏器的患者禁用此疗法。""",
    
    """【2024-12-31 药品召回通知】
    由于生产线遭受微生物污染，X药业集团紧急召回批次号为#20241101的“复方感冒灵颗粒”。
    风险提示：服用受污染药品可能导致严重的细菌性肠胃炎。
    建议：已购买该批次药品的患者请立即停止服用，并联系药店退款。"""
]

@st.cache_resource
def init_rag(thinking_mode=True):
    if not os.path.exists(WORKING_DIR):
        os.mkdir(WORKING_DIR)
    
    api_key = os.environ.get("ZHIPUAI_API_KEY")
    if api_key is None:
        raise Exception("Please set ZHIPU_API_KEY in your environment")
    
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=zhipu_complete,
        llm_model_name="glm-4.7",
        llm_model_max_async=4,
        chunk_token_size=512,
        llm_model_max_token_size=32768,
        llm_model_kwargs={"thinking": {"type": "enabled"}} if thinking_mode else {"thinking": {"type": "disabled"}},
        embedding_func=EmbeddingFunc(
            embedding_dim=1024,
            max_token_size=8192,
            func=lambda texts: ollama_embedding(
                texts,
                embed_model="quentinz/bge-large-zh-v1.5",
                host="http://localhost:11434",
            )
        ),
    )
    return rag

def visualize_graph(rag_instance, query_entity=None):
    """
    生成知识图谱的可视化HTML
    """
    try:
        # 尝试获取图对象，优先使用内存中的，否则尝试读取文件
        G = None
        # 修正：rag.chunk_entity_relation_graph 通常是 NetworkXStorage 实例
        # 它的底层 networkx 图对象存储在 _graph 属性中
        storage_inst = getattr(rag_instance, 'chunk_entity_relation_graph', None)
        
        if storage_inst:
            if hasattr(storage_inst, '_graph'):
                G = storage_inst._graph
            elif isinstance(storage_inst, nx.Graph):
                G = storage_inst
        
        if G is None or len(G.nodes) == 0:
            graph_path = os.path.join(WORKING_DIR, "graph_chunk_entity_relation.graphml")
            if os.path.exists(graph_path):
                G = nx.read_graphml(graph_path)
        
        if G is None or len(G.nodes) == 0:
            return None, "暂无图谱数据"

        # --- 新增：注入时间信息 ---
        try:
            vdb_path = os.path.join(WORKING_DIR, "vdb_entities.json")
            if os.path.exists(vdb_path):
                with open(vdb_path, 'r', encoding='utf-8') as f:
                    vdb_data = json.load(f)
                
                # 构建 实体名 -> 时间 的映射
                entity_time_map = {item["entity_name"]: item.get("__created_at__") 
                                 for item in vdb_data.get("data", []) 
                                 if "entity_name" in item}

                # 遍历图节点并注入时间信息
                for node_id in G.nodes():
                    # 注意：G中的节点ID通常带引号，如 '"流感"'
                    # vdb中的entity_name也通常带引号
                    created_at = entity_time_map.get(str(node_id))
                    
                    # 获取现有属性
                    node_attrs = G.nodes[node_id]
                    # 去除可能存在的引号，用于显示
                    clean_name = str(node_id).strip('"')

                    if created_at:
                        dt = datetime.datetime.fromtimestamp(created_at)
                        time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                        date_str = dt.strftime('%Y-%m-%d')
                        
                        # 设置 label: 名字 + 换行 + 日期
                        node_attrs["label"] = f"{clean_name}\n{date_str}"
                        
                        desc = node_attrs.get("description", "")
                        
                        # 避免重复添加 description
                        if "收录时间" not in desc:
                            new_desc = f"{desc}\n\n【收录时间】: {time_str}"
                            node_attrs["description"] = new_desc
                            # Pyvis默认使用title作为hover提示
                            node_attrs["title"] = new_desc
                    else:
                        # 如果没有时间，且没有设置过label，则设置一个不带引号的label
                        if "label" not in node_attrs:
                            node_attrs["label"] = clean_name
                            
        except Exception as e:
            print(f"Warning: Failed to inject time info: {e}")
        # ------------------------

        # 子图过滤逻辑
        if query_entity:
            # 模糊匹配节点ID
            nodes = [n for n in G.nodes() if query_entity in str(n)]
            if nodes:
                # 提取一跳邻居
                subgraph_nodes = set(nodes)
                for n in nodes:
                    subgraph_nodes.update(G.neighbors(n))
                G = G.subgraph(subgraph_nodes)
            else:
                return None, f"未找到包含 '{query_entity}' 的节点"
        else:
            # 默认只显示前100个节点，防止浏览器卡死
            if len(G.nodes) > 100:
                G = G.subgraph(list(G.nodes())[:100])

        # 使用 Pyvis 生成可视化
        net = Network(height="500px", width="100%", bgcolor="#222222", font_color="white")
        # 避免 notebook 模式导致的问题
        net.force_atlas_2based()
        net.from_nx(G)
        
        # 保存到临时文件
        path = os.path.join(WORKING_DIR, "temp_graph.html")
        net.save_graph(path)
        
        with open(path, 'r', encoding='utf-8') as f:
            html_string = f.read()
            
        return html_string, "Success"
        
    except Exception as e:
        return None, str(e)

def main(is_admin, usname):
    with st.sidebar:
        col1, col2 = st.columns([0.6, 0.6])
        with col1:
            st.image(os.path.join("img", "logo.jpg"), width="stretch")

        # --- 新增：深度思考开关 (放在顶部以控制初始化) ---
        enable_thinking = st.checkbox("启用深度思考 (GLM-4.7)", value=True, help="开启后模型将进行深度推理，回复质量更高但速度较慢。")

        st.caption(
            f"""<p align="left">欢迎您，{'管理员' if is_admin else '用户'}{usname}！</p>""",
            unsafe_allow_html=True,
        )
    
    # 初始化RAG (带缓存，依赖深度思考开关)
    rag = init_rag(enable_thinking)

    st.title(f"医疗智能问答机器人 (基于动态知识图谱)")

    with st.sidebar:

        # 对话窗口管理
        if 'chat_windows' not in st.session_state:
            st.session_state.chat_windows = [[]]
            st.session_state.messages = [[]]

        if st.button('新建对话窗口'):
            st.session_state.chat_windows.append([])
            st.session_state.messages.append([])

        window_options = [f"对话窗口 {i + 1}" for i in range(len(st.session_state.chat_windows))]
        selected_window = st.selectbox('请选择对话窗口:', window_options)
        active_window_index = int(selected_window.split()[1]) - 1

        # --- 改造点1：动态更新模块 ---
        st.markdown("---")
        st.subheader("🌐 动态知识注入 (模拟从网页获取)")
        st.info("用于演示：模拟从新闻流中获取最新流感资讯并更新图谱。")
        selected_news = st.selectbox("选择新闻事件", FAKE_NEWS_DATA)

        if st.button("注入并更新知识库"):
            with st.spinner("正在抽取实体关系并更新图谱..."):
                # --- 新增调试代码 ---
                print(f"【DEBUG】正在插入的新闻长度: {len(selected_news)} 字符")
                print(f"【DEBUG】新闻前50字: {selected_news[:50]}")
                # ------------------
                rag.insert(selected_news)
                st.success("更新成功！新知识已融入图谱。")
                # 强制刷新图谱缓存（如果有必要）
        
        # --- 改造点2：图谱可视化入口 ---
        st.markdown("---")
        st.subheader("🕸️ 知识图谱可视化")
        vis_entity = st.text_input("输入实体查看关联子图", placeholder="留空查看全局概览")
        if st.button("生成/刷新拓扑图"):
            st.session_state.show_graph = True
            st.session_state.vis_entity = vis_entity

        if st.button("返回登录"):
            st.session_state.logged_in = False
            st.session_state.admin = False
            st.rerun()

    # 主界面逻辑
    current_messages = st.session_state.messages[active_window_index]

    # 显示图谱 (如果被触发)
    if st.session_state.get('show_graph', False):
        with st.expander("🕸️ 当前知识图谱拓扑结构", expanded=True):
            html_data, msg = visualize_graph(rag, st.session_state.get('vis_entity'))
            if html_data:
                components.html(html_data, height=520, scrolling=True)
            else:
                st.warning(f"可视化生成失败或无数据: {msg}")
            
            if st.button("关闭图谱"):
                st.session_state.show_graph = False
                st.rerun()

    # 显示历史消息
    for message in current_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 处理用户输入
    if query := st.chat_input("请输入您的医疗问题...", key=f"chat_input_{active_window_index}"):
        current_messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        response_placeholder = st.empty()
        response_placeholder.text("正在检索知识图谱并生成回答...")

        # RAG 查询
        # 使用 hybrid 模式以利用图谱和向量的综合优势
        response = rag.query(query, param=QueryParam(mode="hybrid", thinking=enable_thinking))
        
        print('生成回答：', response)
        response_placeholder.empty()

        with st.chat_message("assistant"):
            st.markdown(response)

        current_messages.append({"role": "assistant", "content": response})

    st.session_state.messages[active_window_index] = current_messages
