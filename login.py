import os
import sys

# 设置环境变量，禁用Streamlit的文件监视， 这一步要在导入streamlit之前设置
os.environ["STREAMLIT_SERVER_ENABLE_STATIC_SERVING"] = "false"

# 添加LightRAG目录到系统路径 因为是导入的项目，需要添加路径，不然报错找不到module named lightragPkg这个文件夹
sys.path.append(os.path.join(os.path.dirname(__file__), 'LightRAG'))

import streamlit as st
from webui import main

if __name__ == "__main__":
    # 设置页面配置（可选，提升体验）
    st.set_page_config(
        page_title="医疗新闻智能问答系统",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 直接进入主界面，默认以管理员身份无需登录
    # 参数: is_admin=True, usname="User"
    main(True, "User")
