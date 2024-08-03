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

doc_processor  = DocProcessor()
from page_layout import page_config
page_config()

# 使用 NameNode 的主机名和端口号，确保这些在容器网络中可达
hdfs_url = 'http://namenode:9870'
hdfs_user = 'hadoop'  # 替换为您的 HDFS 用户名
fp = '/hadoop-data/'

# 初始化 HDFS 客户端
client = InsecureClient(hdfs_url, user=hdfs_user)

datatype = ["file uploading", "data cleaning", "metadata extraction"]
main_page = st.sidebar.radio("Data processing", datatype)



if main_page == datatype[0]:
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
        
elif main_page == datatype[1]:
    import streamlit as st
    from hdfs import InsecureClient
    from pdfminer.high_level import extract_text, extract_text_to_fp
    import io
    from pdf2image import convert_from_bytes
    import os
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter

    current_dir = os.path.dirname(os.path.abspath(__file__))
    import sys
    sys.path.append(current_dir)
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
    from page_layout import page_config
    from DataCleaner import DataCleaner
    from llm import improve_text

    from DataTypeProcessing import PdfProcessor, DocxProcessor, DocProcessor
    from docx import Document

    # 初始化 session state
    if 'show_col2' not in st.session_state:
        st.session_state['show_col2'] = False

    # page_config()
    # 示例使用
    data_cleaner = DataCleaner()


    # HDFS 配置
    hdfs_url = 'http://namenode:9870'
    hdfs_user = 'hadoop'  # 替換為您的 HDFS 用戶名
    client = InsecureClient(hdfs_url, user=hdfs_user)

    # 列出 HDFS 中的文件
    file_list = client.list('/hadoop-data')
    print(f"Files in HDFS: {file_list}")

    record_file_path = '/hadoop-data/new_uploaded.txt'
    with client.read(record_file_path) as record_file:
        # 读取文件中的所有行，并解码为字符串，同时去掉每行末尾的换行符
        uploaded_files = [line.decode('utf-8').strip() for line in record_file]


    # 打印读取到的文件名列表
    for filename in uploaded_files:
        print(f"Uploaded file: {filename}")


    # 在側邊欄中選擇文件
    file_list.append("請選擇文件")
    uploaded_files.append("請選擇文件")
    # the last of the list become the first and the first become the default
    file_list = file_list[::-1]
    uploaded_files = uploaded_files[::-1]

    # 初始化 session state 中的变量
    if 'selected_file' not in st.session_state:
        st.session_state.selected_file = ''
    if 'all_file_select' not in st.session_state:
        st.session_state.all_file_select = "請選擇文件"
    if 'newest_file_select' not in st.session_state:
        st.session_state.newest_file_select = "請選擇文件"
    if "cleaned" not in st.session_state:
        st.session_state.cleaned = ""

    # 根据用户选择的文件进行处理
    def process_selected_file(selected_file):
        # determine the file type
        file_type = selected_file.split('.')[-1]
        print(f"File type: {file_type}")

        # 讀取文件內容
        hdfs_path = '/hadoop-data/' + selected_file

        with client.read(hdfs_path) as reader:
            content = reader.read()  # 以二進制模式讀取

        if file_type == 'pdf':
            pdf_processor = PdfProcessor()

            text_content, show_col2 = pdf_processor.process_pdf(content)
            if show_col2:
                st.session_state['show_col2'] = True
            else:
                st.session_state['show_col2'] = False
                
            cols = st.columns(3)
            with cols[0]:
                st.subheader('原始文件內容')
                images = convert_from_bytes(content)
                for image in images:
                    st.image(image)

            # with col2:
            #     st.subheader('圖片處理')
            #     if st.session_state['show_col2']:
            #         images = convert_from_bytes(content)
            #         for image in preprocessed_images:
            #             st.image(image)
            #     else:
            #         st.write('非圖檔')
                    
            with cols[1]:
                st.subheader('提取文本')
                st.write(text_content)
                    
            with cols[2]:
                st.subheader('說明擷取')
            
                cleaned = data_cleaner.data_cleaning(text_content)
                
                if st.session_state['show_col2']:
                    cleaned = improve_text(cleaned)
                    st.write(cleaned)
                    print("OCR with llm")
                else:
                    st.write(cleaned)
                    print("Text with cleaning tool")
                st.session_state.cleaned = cleaned
                # add the button that triggers the uploading to HDFS
                # if st.button('Upload to HDFS'):
                #     # create a folder in HDFS if not existed
                #     client.makedirs('/cleaned')

                #     hdfs_path = '/cleaned/' + file_read
                #     with client.write(hdfs_path, overwrite=True) as writer:
                #         writer.write(improved)  # 直接將二進制數據寫入
                #     st.write(f'文件已上傳到 HDFS: {hdfs_path}')

        elif file_type == 'docx':

            docx_file = io.BytesIO(content)
            # 使用 python-docx 读取文件内容
            document = Document(docx_file)
            text_content = "\n".join([para.text for para in document.paragraphs])

            cols = st.columns(2)
            with cols[0]:
                st.subheader('原始文件內容')
                st.write(text_content)

            with cols[1]:
                st.subheader('說明擷取')
                cleaned = data_cleaner.data_cleaning(text_content)
                st.write(cleaned)
                st.session_state.cleaned = cleaned
                
        else:
            with client.read(hdfs_path) as record_file:
                # 读取文件中的所有行，并解码为字符串，同时去掉每行末尾的换行符
                doc_content = [line.decode('utf-8').strip() for line in record_file]
            
            text_content = "\n".join(doc_content)
            
            cols = st.columns(3)
            with cols[0]:
                st.subheader('原始文件內容')
                st.write(doc_content)
                
            with cols[1]:
                st.subheader('排版後內容')
                st.write(text_content)
                
                
            with cols[2]:
                st.subheader('說明擷取')
                cleaned = data_cleaner.data_cleaning(text_content)
                st.write(cleaned)
                st.session_state.cleaned = cleaned

        
        
    # 更新选择的文件
    def update_selected_file(selection_type):
        if selection_type == 'all':
            st.session_state.selected_file = st.session_state.all_file_select
        elif selection_type == 'new':
            st.session_state.selected_file = st.session_state.newest_file_select

    # 在侧边栏中选择文件
    st.sidebar.selectbox("全部文件", file_list, key="all_file_select", on_change=update_selected_file, args=('all',))
    st.sidebar.selectbox("最新文件", uploaded_files, key="newest_file_select", on_change=update_selected_file, args=('new',))


    # 如果有选择的文件，进行处理并显示内容
    if st.session_state.selected_file and st.session_state.selected_file != "請選擇文件":
        process_selected_file(st.session_state.selected_file)
    else:
        st.write("请选择一个文件进行处理。")
        

elif main_page == datatype[2]:
    from hivedb import HiveDB
    from MetaDataExtractor import MetaDataExtractor
    metadata_extractor = MetaDataExtractor()
    hive_db = HiveDB()
    hive_db.use_database('test')
    table_name = 'testdf2_table'
    # read the table
    filename_list = hive_db.read_columns('filename', table_name)
    
    select_file = st.sidebar.selectbox("Select a file", filename_list)
    
    # make sure the file is selected
    if select_file:
        st.session_state.selected_file = select_file
        cleaned = hive_db.read_columns_by_condition('cleaned', table_name, 'filename', select_file[0])
        cleaned = cleaned[0][0]
        st.subheader("Cleaned text")
        st.write(cleaned)
        
    else:
        st.write("Please select a file")
    
    # print(st.session_state.cleaned)
    # print(st.session_state.selected_file)
    metadata = metadata_extractor.extract_metadata(select_file[0], cleaned)
    st.subheader("Metadata extraction")
    st.write(metadata)
