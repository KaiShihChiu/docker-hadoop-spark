# 使用官方的 Python 基础镜像
FROM python:3

# 设置工作目录
WORKDIR /python-test

# 复制应用程序文件到工作目录
COPY test.py /python-test/

# 安装Streamlit及其依赖
RUN pip install streamlit numpy pandas hdfs

# 暴露 Streamlit 默认端口
EXPOSE 1000

# 运行 Streamlit 应用
CMD ["tail", "-f", "/dev/null"]
