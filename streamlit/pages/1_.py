import streamlit as st
from pathlib import Path
import sys
import os
from hdfs import InsecureClient
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
import pytesseract
import io
from PIL import Image

# 獲取當前文件的路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
# 將文件所在的目錄添加到 sys.path 中
sys.path.append(current_dir)
from page_layout import page_config
page_config()

# 使用 NameNode 的主机名和端口号，确保这些在容器网络中可达
hdfs_url = 'http://namenode:9870'
hdfs_user = 'hadoop'  # 替换为您的 HDFS 用户名

# 初始化 HDFS 客户端
client = InsecureClient(hdfs_url, user=hdfs_user)

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
    st.session_state.source_docs = st.file_uploader(label="Upload Documents", type=["pdf", "png", "jpeg", "jpg", "docx"], accept_multiple_files=True)

def extract_text_from_images(images):
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image, lang='eng+chi_tra')
    return text

# 处理上传的文档
def process_documents():
    for uploaded_file in st.session_state.source_docs:
        if uploaded_file is not None:
            # 獲取文件內容作為二進制數據
            file_bytes = uploaded_file.read()

            hdfs_path = '/hadoop-data/' + uploaded_file.name
            print(f'Writing data to {hdfs_path} on HDFS...')
            with client.write(hdfs_path, overwrite=True) as writer:
                writer.write(file_bytes)  # 直接將二進制數據寫入

            # 提取 PDF 文件中的文本
            pdf_text = extract_text(io.BytesIO(file_bytes))

            # 顯示提取的文本內容
            st.markdown(f"### Extracted Text from {uploaded_file.name}:")
            st.text(pdf_text)

    st.session_state.success_message = "Documents uploaded and read successfully."

if st.button('Upload Documents'):
    process_documents()

input_field()

if st.session_state.success_message:
    st.success(st.session_state.success_message)
