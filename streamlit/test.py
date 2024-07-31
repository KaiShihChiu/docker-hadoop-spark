from hdfs import InsecureClient

# 使用 NameNode 的主机名和端口号，确保这些在容器网络中可达
hdfs_url = 'http://namenode:9870'
hdfs_user = 'hadoop'  # 替换为您的 HDFS 用户名

# 初始化 HDFS 客户端
client = InsecureClient(hdfs_url, user=hdfs_user)

# 列出 HDFS 中的文件
file_list = client.list('/hadoop-data')
file_read = file_list[0]
print(f'Files in /hadoop-data: {file_read}')

# 读取文件内容
hdfs_path = '/hadoop-data/' + file_read
with client.read(hdfs_path) as reader:
    content = reader.read()  # 以二进制模式读取

# 打印文件内容的类型和大小
print(f'Content type: {type(content)}, Content size: {len(content)} bytes')

# 如果需要处理 PDF 文件的内容，可以继续使用上面的 Streamlit 应用代码
# 例如，将 PDF 文件保存到本地并提取文本
import tempfile
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import io

# 保存文件到临时文件
with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
    temp_pdf.write(content)
    temp_pdf_path = temp_pdf.name

# 提取 PDF 文件中的文本
pdf_text = extract_text(temp_pdf_path)
# 将 PDF 转换为图像
images = convert_from_path(temp_pdf_path)

# 提取图像中的文本
def extract_text_from_images(images):
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image, lang='eng+chi_tra')
    return text

ocr_text = extract_text_from_images(images)

# 合并文本
full_text = pdf_text + "\n\n" + ocr_text

# 打印提取的文本
print(f'Extracted Text:\n{full_text}')

# 删除临时文件
import os
os.remove(temp_pdf_path)


import pyhive.hive

