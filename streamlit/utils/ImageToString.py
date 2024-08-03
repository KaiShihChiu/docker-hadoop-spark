
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter


crop_ratio = (0.1, 0.05, 0.9, 0.9)  # 示例比例，根據實際情況調整
# 圖像預處理和 OCR 提取文本
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

def image_to_string(pdf_content)

    images = convert_from_bytes(pdf_content)
    text_content = ""
    preprocessed_images = []
    for image in images:
        preprocessed_image = preprocess_image(image, crop_ratio)
        preprocessed_images.append(preprocessed_image)
        text = pytesseract.image_to_string(preprocessed_image, lang='chi_tra')
        text_content += text + "\n"
        
    return text_content, preprocessed_images