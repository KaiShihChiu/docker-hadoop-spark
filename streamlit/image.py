import io
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance
import streamlit as st

class ImgProcessor:
    def __init__(self, image_bytes):
        self.image = Image.open(io.BytesIO(image_bytes))
    
    def convert_to_grayscale(self):
        self.image = self.image.convert('L')
        return self.image

    def enhance_contrast(self, factor=2):
        enhancer = ImageEnhance.Contrast(self.image)
        self.image = enhancer.enhance(factor)
        return self.image

    def upsample_image(self, scale_percent=200):
        image_np = np.array(self.image)
        width = int(image_np.shape[1] * scale_percent / 100)
        height = int(image_np.shape[0] * scale_percent / 100)
        dim = (width, height)
        self.image = cv2.resize(image_np, dim, interpolation=cv2.INTER_CUBIC)
        return self.image

    def sharpen_image(self):
        kernel = np.array([[0, -1, 0], 
                           [-1, 5, -1], 
                           [0, -1, 0]])
        self.image = cv2.filter2D(np.array(self.image), -1, kernel)
        return self.image

    def adaptive_threshold(self):
        if len(np.array(self.image).shape) == 2 or np.array(self.image).shape[2] == 1:
            self.image = cv2.cvtColor(np.array(self.image), cv2.COLOR_GRAY2BGR)
        gray = cv2.cvtColor(np.array(self.image), cv2.COLOR_BGR2GRAY)
        self.binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 9)
        return self.binary

    def remove_horizontal_lines(self):
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
        detect_horizontal = cv2.morphologyEx(self.binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        contours, _ = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            [x, y, w, h] = cv2.boundingRect(contour)
            if w > 120:
                cv2.drawContours(np.array(self.image), [contour], -1, (255, 255, 255), thickness=cv2.FILLED)
        return self.image

    def extract_text(self, lang='chi_tra'):
        text = pytesseract.image_to_string(self.image, lang=lang)
        return text

def main():
    # Assuming `content` is your image byte data
    content = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    if content is not None:
        processor = ImgProcessor(content.read())

        with st.container():
            st.subheader("Original Image")
            st.image(processor.image, use_column_width=True)

            processor.convert_to_grayscale()
            st.subheader("Original Text")
            original_text = processor.extract_text()
            st.write(original_text)
            
        with st.container():
            processor.enhance_contrast()
            processor.upsample_image()
            processor.sharpen_image()
            st.subheader("Enhanced Image")
            st.image(processor.image, use_column_width=True)

            enhanced_text = processor.extract_text()
            st.subheader("Enhanced Text")
            st.write(enhanced_text)
            
        with st.container():
            binary_image = processor.adaptive_threshold()
            st.image(binary_image, caption="Binary Image", use_column_width=True)
            
            filtered_image = processor.remove_horizontal_lines()
            st.subheader("Filtered Image")
            st.image(filtered_image, use_column_width=True)

            filtered_text = processor.extract_text()
            st.subheader("Filtered Text")
            st.write(filtered_text)

if __name__ == "__main__":
    main()
