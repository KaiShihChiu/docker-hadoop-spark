import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
import streamlit as st
import subprocess
import os
from docx import Document
# extract images from hdfs 
import io
from PIL import Image
from hdfs import InsecureClient
import pytesseract
st.set_page_config(
    layout="wide"
)
from DataTypeProcessing import ImgProcessor

# 使用 NameNode 的主机名和端口号，确保这些在容器网络中可达
hdfs_url = 'http://namenode:9870'
hdfs_user = 'hadoop'  # 替换为您的 HDFS 用户名
fp = '/hadoop-data/'

# 初始化 HDFS 客户端
client = InsecureClient(hdfs_url, user=hdfs_user)

def extract_imagefiles_from_hdfs():
    # 列出 HDFS 中的文件
    file_list = client.list('/hadoop-data')
    # print(f"Files in HDFS: {file_list}")
    
    # select the filename with .png .jpg .jpeg
    image_files = [file for file in file_list if file.endswith(('.png', '.jpg', '.jpeg'))]
    
    return image_files


img_files = extract_imagefiles_from_hdfs()

st.sidebar.markdown("### Image Files")
selected_file = st.sidebar.selectbox("Select a file", img_files)
    

# 讀取文件內容
hdfs_path = '/hadoop-data/' + selected_file

with client.read(hdfs_path) as reader:
    content = reader.read()

# img_processor = ImgProcessor()
# process_img, text_content = img_processor.process_img(content)

# def ocr_image(image_bytes):
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

cols = st.columns(5)

# 創建 3x3 的網格
cols = [st.columns(3) for _ in range(3)]

# 填充網格的每個單元格
# for i in range(3):
#     for j in range(3):
#         with cols[i][j]:
#             st.write(f"Cell ({i+1}, {j+1})")
#             # 你可以在這裡放置其他的 Streamlit 元素，比如：
#             # st.image("path/to/image.png")
#             # st.button("Click me")
#             # st.text_input("Enter text")

# def remove_underline(img):


import cv2
import numpy as np

with cols[0][0]:
    st.subheader("Original Image")
    st.image(content, use_column_width=True)
    image = Image.open(io.BytesIO(content))
    image = image.convert('L')
    
with cols[1][0]:
    st.subheader("Original Text")
    text = pytesseract.image_to_string(image, lang='chi_tra')  # 'chi_tra' 是繁體中文的語言代碼
    st.write(text)
    
    
with cols[0][1]:
    # 增強對比度
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    
    image = np.array(image)
    scale_percent = 200  # 將圖像放大到原來的兩倍
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    upsampled = cv2.resize(image, dim, interpolation=cv2.INTER_CUBIC)

    # 銳化圖像
    kernel = np.array([[0, -1, 0], 
                       [-1, 5,-1], 
                       [0, -1, 0]])
    image = cv2.filter2D(upsampled, -1, kernel)
    st.subheader("Enhanced Image")
    st.image(image, use_column_width=True)
    
with cols[1][1]:
    st.subheader("Enhanced Text")
    text = pytesseract.image_to_string(image, lang='chi_tra')  # 'chi_tra' 是繁體中文的語言代碼
    st.write(text)
    
with cols[0][2]:
    image = np.array(image)

    if len(image.shape) == 2 or image.shape[2] == 1:
        # 如果是灰度圖像，將其轉換為 BGR
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    # 將圖像轉換為灰度圖像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 使用自適應閾值進行二值化
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 9)
    
    # st.image(binary)
    
    # 定義水平結構化元素
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
    detect_horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # 找到輪廓並移除橫線
    contours, _ = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        [x, y, w, h] = cv2.boundingRect(contour)
        if w > 120:  # 根據實際情況調整閾值
            cv2.drawContours(image, [contour], -1, (255, 255, 255), thickness=cv2.FILLED)

    # image = remove_underline(image)
    # image = image.filter(ImageFilter.MedianFilter())
    st.subheader("Filtered Image")
    st.image(image, use_column_width=True)
    
with cols[1][2]:
    text = pytesseract.image_to_string(image, lang='chi_tra')  # 'chi_tra' 是繁體中文的語言代碼
    st.subheader("Filtered Text")
    st.write(text)



with cols[2][0]:
    from DataTypeProcessing import ImgProcessor
    st.subheader("Final Text")
    img_processor = ImgProcessor(content)
    text = img_processor.extract_text()
    st.write(text)


# with cols[0]:
#     st.image(content, use_column_width=True)
    
# with cols[1]:
#     st.image(process_img, use_column_width=True)
       
# with cols[2]:

    
#     text_content = ocr_image(content)
#     # text = pytesseract.image_to_string(process_img, lang='chi_tri')  # 'chi_sim' 是簡體中文的語言代碼

#     st.write(text_content)
    
    



