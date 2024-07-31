import socket

try:
    ip_address = socket.gethostbyname('localhost')
    print(f"localhost resolves to {ip_address}")
except socket.error as e:
    print(f"Failed to resolve localhost: {e}")

from hdfs import InsecureClient

hdfs_url = 'http://172.21.0.3:9870'

client = InsecureClient(hdfs_url, user=hdfs_user)

# 測試連接
try:
    client.status('/')
    print("Connected to HDFS successfully.")
except Exception as e:
    print(f"Failed to connect to HDFS: {e}")

# # 使用 NameNode 的主机名和端口号，确保这些在容器网络中可达
# hdfs_url = 'http://172.21.0.3:9870'
# hdfs_user = 'hadoop'  # 替换为您的 HDFS 用户名

# # 初始化 HDFS 客户端
# client = InsecureClient(hdfs_url, user=hdfs_user)

# # 要写入的数据
# data = 'Hello, HDFS from Python!'

# # 目标文件路径
# hdfs_path = '/hadoop-data/testfile_python_external.txt'

# # 写入数据到 HDFS
# with client.write(hdfs_path, encoding='utf-8', overwrite=True) as writer:
#     writer.write(data)

# print(f'Data written to {hdfs_path} on HDFS.')


