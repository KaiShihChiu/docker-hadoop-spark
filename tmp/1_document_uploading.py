import streamlit as st
from pathlib import Path
import sys
import os
# 獲取當前文件的路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
# 將文件所在的目錄添加到 sys.path 中
sys.path.append(current_dir)
from page_layout import page_config
page_config()

from hdfs import InsecureClient

# # 连接到 HDFS
# hdfs_url = 'http://localhost:50070'
# client = InsecureClient(hdfs_url, user='kaishihchiu')

# # 创建一个目录
# hdfs_path = '/home/kaishihchiu/hdfs/data'
# client.makedirs(hdfs_path)


st.markdown("# File Uploading")
st.sidebar.markdown("""
    ### The file will be: 
    - stored in the Datalake
    - transformed (if needed) into a text-based format
    - stored in the relational database """)


st.markdown(
    """ ## This step allows you to upload the file type of PDF, PNG, JPEG, and Word. 
    """
)

# 定义临时目录
TMP_DIR = Path(__file__).resolve().parent.joinpath('data', 'pdf')
TMP_DIR.mkdir(parents=True, exist_ok=True)

if 'success_message' not in st.session_state:
    st.session_state.success_message = None

# 文件上传输入框
def input_field():
    st.session_state.source_docs = st.file_uploader(label="Upload Documents", type="pdf", accept_multiple_files=True)

# 处理上传的文档
def process_documents():
    for uploaded_file in st.session_state.source_docs:
        if uploaded_file is not None:
            # with client.write(os.path.join(hdfs_path, uploaded_file.name), encoding='utf-8') as writer:
            #     writer.write(uploaded_file.read())
            file_path = TMP_DIR / uploaded_file.name
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.read())
                
    st.session_state.success_message = "Documents uploaded successfully."

# 清理 TMP_DIR 目录
# def clear_temp_dir():
#     for item in TMP_DIR.iterdir():
#         if item.is_file():
#             item.unlink()

# 界面布局
# clear_temp_dir()  # 每次运行时清理目录
input_field()
# 设置按钮和消息的布局
col1, col2, col3 = st.columns([1, 2, 2])

with col1:
    st.button("Submit Documents", on_click=process_documents)

with col2:
    if  st.session_state['success_message'] == "Documents uploaded successfully.":
        st.success(st.session_state.success_message)
        st.session_state['success_message'] = None