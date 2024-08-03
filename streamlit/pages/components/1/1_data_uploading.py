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
from docx import Document
current_dir = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.append(current_dir)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from DataTypeProcessing import DocProcessor

def data_uploading():
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
    # TMP_DIR = Path(__file__).resolve().parent.joinpath('data', 'pdf')
    # TMP_DIR.mkdir(parents=True, exist_ok=True)

    if 'success_message' not in st.session_state:
        st.session_state.success_message = None

    # 文件上传输入框
    def input_field():
        st.session_state.source_docs = st.file_uploader(label="Upload Documents", type=["pdf", "png", "jpeg", "jpg", "docx", ".doc"], accept_multiple_files=True)

    # 处理上传的文档
    def process_documents():
        filenames = ""
        for uploaded_file in st.session_state.source_docs:
            if uploaded_file is not None:
                # 獲取文件內容作為二進制數據
                file_bytes = uploaded_file.read()
                
                fn = uploaded_file.name
                file_type = fn.split('.')[-1]
                
                if file_type in ["doc"]:
                    unique_text = doc_processor.process_docx(file_bytes, fn)
                    # hdfs_path = fp + fn.replace('.doc', '.txt')
                    # print(hdfs_path)
                    # print(unique_text)
                else:
                    unique_text = file_bytes

                hdfs_path = fp + fn

                with client.write(hdfs_path, overwrite=True) as writer:
                    writer.write(unique_text)  # 直接將二進制數據寫入

                filenames += fn + "\n"

        fp_text = fp + "new_uploaded.txt"
        with client.write(fp_text, overwrite=True) as writer:
            writer.write(filenames)  # 直接將二進制數據寫入


        st.session_state.success_message = "Documents uploaded and read successfully."



    input_field()

    if st.button('Upload Documents'):
        process_documents()
    if st.session_state.success_message:
        st.success(st.session_state.success_message)