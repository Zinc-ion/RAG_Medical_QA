import streamlit as st
import ollama
import py2neo
import random
import re
import os
import sys
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
    """【2024-12-29 突发卫生事件】
    某地疾控中心报告发现一种新型流感病毒变异株“H9N9-Beta”。
    症状表现：该变异株除常规流感症状外，显著特征为持续性关节剧痛和结膜充血。
    治疗方案：初步临床试验显示，抗病毒药物“奥司他韦”联合新药“V-2024”具有显著疗效。
    传播途径：主要通过呼吸道飞沫传播，潜伏期缩短至12小时。""",
    
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
def init_rag():
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
        if hasattr(rag_instance, 'chunk_entity_relation_graph'):
            G = rag_instance.chunk_entity_relation_graph
        
        if G is None or len(G.nodes) == 0:
            graph_path = os.path.join(WORKING_DIR, "graph_chunk_entity_relation.graphml")
            if os.path.exists(graph_path):
                G = nx.read_graphml(graph_path)
        
        if G is None or len(G.nodes) == 0:
            return None, "暂无图谱数据"

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
    # 初始化RAG (带缓存)
    rag = init_rag()
    
    st.title(f"医疗智能问答机器人 (基于动态知识图谱)")

    with st.sidebar:
        col1, col2 = st.columns([0.6, 0.6])
        with col1:
            st.image(os.path.join("img", "logo.jpg"), use_container_width=True)

        st.caption(
            f"""<p align="left">欢迎您，{'管理员' if is_admin else '用户'}{usname}！</p>""",
            unsafe_allow_html=True,
        )

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
        st.subheader("🌐 动态知识注入 (模拟)")
        st.info("用于演示：模拟从新闻流中获取最新医疗资讯并更新图谱。")
        selected_news = st.selectbox("选择模拟新闻事件", FAKE_NEWS_DATA)
        
        if st.button("注入并更新知识库"):
            with st.spinner("正在抽取实体关系并更新图谱..."):
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
        response = rag.query(query, param=QueryParam(mode="hybrid"))
        
        print('生成回答：', response)
        response_placeholder.empty()

        with st.chat_message("assistant"):
            st.markdown(response)

        current_messages.append({"role": "assistant", "content": response})

    st.session_state.messages[active_window_index] = current_messages
