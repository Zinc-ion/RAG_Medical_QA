import os
import sys

# 设置环境变量，禁用Streamlit的文件监视， 这一步要在导入streamlit之前设置
os.environ["STREAMLIT_SERVER_ENABLE_STATIC_SERVING"] = "false"

# 添加LightRAG目录到系统路径 因为是导入的项目，需要添加路径，不然报错找不到module named lightragPkg这个文件夹
sys.path.append(os.path.join(os.path.dirname(__file__), 'LightRAG'))


import streamlit as st
from user_data_storage import credentials, write_credentials, storage_file, Credentials
from webui import main




# 初始化会话状态
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'admin' not in st.session_state:
    st.session_state.admin = False
if 'usname' not in st.session_state:
    st.session_state.usname = ""
def login_page():
    with st.form("login_form"):
        st.title("登录")
        username = st.text_input("用户名", value="")
        password = st.text_input("密码", value="", type="password")
        submit = st.form_submit_button("登录")
        
        if submit:
            user_cred = credentials.get(username)
            if user_cred and user_cred.password == password:
                st.success("登录成功！")
                st.session_state.logged_in = True
                st.session_state.admin = user_cred.is_admin
                st.session_state.usname = username
                # 将 st.experimental_rerun() 替换为 st.rerun()
                st.rerun()
            else:
                st.error("用户名或密码错误，请重新输入。")

def register_page():
    with st.form("register_form"):
        st.title("注册")
        new_username = st.text_input("设置用户名", value="")
        new_password = st.text_input("设置密码", value="", type="password")
        is_admin = False
        register_submit = st.form_submit_button("注册")
        
        if register_submit:
            if new_username in credentials:
                # 老板st才是expermintal_rerun 新版直接rerun
                st.error("用户名已存在，请使用其他用户名。")
            else:
                new_user = Credentials(new_username, new_password, is_admin)
                credentials[new_username] = new_user
                write_credentials(storage_file, credentials)
                st.success(f"用户 {new_username} 注册成功！请登录。")
                # 将 st.experimental_rerun() 替换为 st.rerun()
                st.rerun()

if __name__ == "__main__":
    if not st.session_state.logged_in:
        # 显示注册和登录选项
        st.sidebar.title("导航")
        app_mode = st.sidebar.selectbox("选择操作", ["登录", "注册"])
        if app_mode == "登录":
            login_page()
        elif app_mode == "注册":
            register_page()
    else:
        main(st.session_state.admin,st.session_state.usname)
