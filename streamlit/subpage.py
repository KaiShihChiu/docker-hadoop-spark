import streamlit as st

# 设置主页面的选项
main_page = st.sidebar.radio("Data processing", ["Data upload", "页面1", "页面2"])

# 子页面选项
if main_page == "Data upload":
    st.title("主页")
    st.write("这是主页的内容。")
elif main_page == "页面1":
    sub_page = st.radio("选择子页面", ["子页面1-1", "子页面1-2"])
    if sub_page == "子页面1-1":
        st.title("页面1 - 子页面1-1")
        st.write("这是页面1的子页面1-1的内容。")
    elif sub_page == "子页面1-2":
        st.title("页面1 - 子页面1-2")
        st.write("这是页面1的子页面1-2的内容。")
elif main_page == "页面2":
    sub_page = st.radio("选择子页面", ["子页面2-1", "子页面2-2"])
    if sub_page == "子页面2-1":
        st.title("页面2 - 子页面2-1")
        st.write("这是页面2的子页面2-1的内容。")
    elif sub_page == "子页面2-2":
        st.title("页面2 - 子页面2-2")
        st.write("这是页面2的子页面2-2的内容。")
