# 使用官方的 Python 基础镜像
FROM python:3

# 设置工作目录
WORKDIR /streamlit

# 复制当前目录内容到工作目录
COPY . .

# 复制 pages 目录内容到容器中的 /streamlit/pages
COPY /pages /streamlit/pages

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && apt-get clean

# 安装依赖包
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 Streamlit 默认端口
EXPOSE 8501

# 运行 Streamlit 应用
# CMD ["streamlit", "run", "app.py"]
CMD ["tail", "-f", "/dev/null"]
