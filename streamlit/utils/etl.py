from hdfs import InsecureClient
from pdfminer.high_level import extract_text, extract_text_to_fp
import io
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.append(current_dir)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))

from DataCleaner import DataCleaner
from llm import improve_text

data_cleaner = DataCleaner()

# HDFS 配置
hdfs_url = 'http://namenode:9870'
hdfs_user = 'hadoop'  # 替換為您的 HDFS 用戶名
client = InsecureClient(hdfs_url, user=hdfs_user)

# extract the file named new_uploaded.txt in hdfs
# 从 HDFS 读取记录文件


# 列出 HDFS 中的文件
file_list = client.list('/hadoop-data')

# 在側邊欄中選擇文件
file_read = st.sidebar.selectbox("選擇文件", file_list, key="file_select")

# 讀取文件內容
hdfs_path = '/hadoop-data/' + file_read

with client.read(hdfs_path) as reader:
    pdf_content = reader.read()  # 以二進制模式讀取

# 提取 PDF 文件中的文本內容
output_string = io.StringIO()
with io.BytesIO(pdf_content) as open_pdf_file:
    extract_text_to_fp(open_pdf_file, output_string)


# 指定裁剪比例（左, 上, 右, 下），值在 0 到 1 之間
crop_ratio = (0.1, 0.05, 0.9, 0.9)  # 示例比例，根據實際情況調整

# 獲取提取的文本内容
text_content = output_string.getvalue()

if len(text_content.strip()) > 0:
    # 如果提取的文本内容不为空，則表示 PDF 文件主要是文字
    print("PDF contains text:")
    print(text_content)
    st.session_state['show_col2'] = False
else:
    # 如果提取的文本内容为空，則表示 PDF 文件主要是圖片
    print("PDF contains images, performing OCR...")

    st.session_state['show_col2'] = True
    
    
    
if 