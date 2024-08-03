from pathlib import Path
import sys
import os
from hdfs import InsecureClient
from pdf2image import convert_from_path
import pytesseract
import io
from PIL import Image, ImageEnhance, ImageFilter
from docx import Document
current_dir = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.append(current_dir)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from pdfminer.high_level import extract_text, extract_text_to_fp
from DataCleaner import DataCleaner
from llm import improve_text
from DataTypeProcessing import PdfProcessor, DocxProcessor, DocProcessor, ImgProcessor
import pandas as pd
import streamlit as st



# 使用 NameNode 的主机名和端口号，确保这些在容器网络中可达
hdfs_url = 'http://namenode:9870'
hdfs_user = 'hadoop'  # 替换为您的 HDFS 用户名
fp = '/hadoop-data/'

# 初始化 HDFS 客户端
client = InsecureClient(hdfs_url, user=hdfs_user)
data_cleaner = DataCleaner()


# 列出 HDFS 中的文件
file_list = client.list('/hadoop-data')
# print(f"Files in HDFS: {file_list}")


# 根据用户选择的文件进行处理
def process_selected_file(selected_file):
    # determine the file type
    file_type = selected_file.split('.')[-1]
    # print(f"File type: {file_type}")

    # 讀取文件內容
    hdfs_path = '/hadoop-data/' + selected_file

    with client.read(hdfs_path) as reader:
        content = reader.read()  # 以二進制模式讀取

    if file_type == 'pdf':
        pdf_processor = PdfProcessor()
        text_content, _ = pdf_processor.process_pdf(content)
        cleaned = data_cleaner.data_cleaning(text_content)

    elif file_type == 'docx':
        docx_processor  = DocxProcessor()
        docx_content = docx_processor.extract_text_from_docx(content)
        cleaned = data_cleaner.data_cleaning(docx_content)
            
    elif file_type in ['png', 'jpg', 'jpeg']:
        img_processor = ImgProcessor(content)
        text = img_processor.extract_text()
        cleaned = data_cleaner.data_cleaning(text)

    elif file_type == 'doc':
        doc_processor  = DocProcessor()
        doc_content = doc_processor.process_doc(content, selected_file)
        cleaned = data_cleaner.data_cleaning(doc_content)
        


# monitor the data processing percentage using streamlit
st.write("Data processing progress")

# 模拟数据处理
for i, selec_file in enumerate(file_list):
    # if selec_file is not a pdf or docx or doc or png or png or jpg or jpeg, skip
    if not selec_file.endswith(('.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg')):
        continue
    else:
        pass
    
    df = pd.DataFrame(columns=['filename', 'cleaned'])

    new_data = pd.DataFrame({
        'filename': [selec_file],
        'cleaned': [process_selected_file(selec_file)]
    })

    df = pd.concat([df, new_data], ignore_index=True)

    # 更新进度条
    progress = int((i + 1) / len(data) * 100)
    progress_bar.progress(progress)
    status_text.text(f"Progress: {progress}%")

st.subheader('Writing to Hive!')
# print(df)
# check hive to see if the file is already there
from hivedb import HiveDB
hive = HiveDB()

# show databases
databases = hive.show_databases()
# create database
db = "govdocs"
hive.create_database(db)
# use the selected database
hive.use_database(db)

# create table
tb = "docs_table"
tb_cols = {
    df.columns[0]: 'STRING',
    df.columns[1]: 'STRING'
}
hive.create_table(tb, tb_cols)

# show tables
tables = hive.show_tables()
st.write(tables)

# save the df to the table
hive.insert_data_from_df(tb, df)

# read the table
# print(hive.read_table(tb))
st.success("Data processing completed!")



# selec_table = st.sidebar.selectbox("Select a table", tables)

# save the selected file in the table for future use


# # check if the file is already in the database
# file_exists = hive.check_file_exists(selected_file)
# if not file_exists:
#     # insert the file into the database
#     hive.insert_file(selected_file, cleaned)
        

    
# elif main_page == datatype[2]:
# from MetaDataExtractor import MetaDataExtractor
# metadata_extractor = MetaDataExtractor()

# print(st.session_state.cleaned)
# print(st.session_state.selected_file)
# metadata = metadata_extractor.extract_metadata(st.session_state.selected_file, st.session_state.cleaned)
# st.write("Metadata extraction")
