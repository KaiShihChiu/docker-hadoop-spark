from pyspark.sql import SparkSession
from hdfs import InsecureClient
from pdfminer.high_level import extract_text_to_fp, extract_text
from pdf2image import convert_from_bytes
from PIL import Image, ImageEnhance
import pytesseract
import pandas as pd
import io
from pyspark.sql.types import StructType, StructField, StringType

# 初始化 Spark 会话
spark = SparkSession.builder \
    .appName("PDF to Parquet ETL") \
    .getOrCreate()

# 初始化 HDFS 客户端
hdfs_url = 'http://namenode:9870'
hdfs_user = 'hadoop'
client = InsecureClient(hdfs_url, user=hdfs_user)
new_dir_path = '/parquet'
client.makedirs(new_dir_path)

# 读取 HDFS 中的文件列表
file_list = client.list('/hadoop-data')

def preprocess_image(image, crop_ratio):
    # 灰度化
    image = image.convert('L')
    width, height = image.size
    # 按比例裁剪圖片
    left = width * crop_ratio[0]
    upper = height * crop_ratio[1]
    right = width * crop_ratio[2]
    lower = height * crop_ratio[3]
    image = image.crop((left, upper, right, lower))
    # 增強對比度
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    # 二值化
    image = image.point(lambda x: 0 if x < 220 else 255, '1')
    return image

def process_pdf(file_read):
    hdfs_path = '/hadoop-data/' + file_read

    with client.read(hdfs_path) as reader:
        pdf_content = reader.read()  # 以二进制模式读取

    # 提取 PDF 文件中的文本内容
    output_string = io.StringIO()
    with io.BytesIO(pdf_content) as open_pdf_file:
        extract_text_to_fp(open_pdf_file, output_string)

    # 獲取提取的文本内容
    text_content = output_string.getvalue()

    if len(text_content.strip()) <= 0:
        # 如果提取的文本内容为空，則表示 PDF 文件主要是圖片
        print("PDF contains images, performing OCR...")
        images = convert_from_bytes(pdf_content)
        text_content = ""
        crop_ratio = (0.1, 0.05, 0.9, 0.9)  # 示例比例，根據實際情況調整

        for image in images:
            preprocessed_image = preprocess_image(image, crop_ratio)
            text = pytesseract.image_to_string(preprocessed_image, lang='chi_tra')
            text_content += text + "\n"

    return file_read, text_content

# 使用 Spark 并行处理 PDF 文件
num_partitions = 4  # 指定分区数
rdd = spark.sparkContext.parallelize(file_list, num_partitions)
processed_rdd = rdd.map(process_pdf)

# 将 RDD 转换为 DataFrame
schema = StructType([
    StructField("filename", StringType(), True),
    StructField("content", StringType(), True)
])

processed_df = spark.createDataFrame(processed_rdd, schema)

# 将数据写入 HDFS 的 Parquet 文件
output_path = f"hdfs://namenode:9870/parquet/output.parquet"
processed_df.write.parquet(output_path, mode='overwrite')

# 读取并显示 Parquet 文件中的数据
parquet_df = spark.read.parquet(output_path)
parquet_df.show(truncate=False)

# 停止 Spark 会话
spark.stop()
