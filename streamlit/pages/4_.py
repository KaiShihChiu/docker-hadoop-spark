import pytesseract
from PIL import Image
import io
from pathlib import Path
# from langchain_community.document_loaders import DirectoryLoader
import streamlit as st
import fitz  # PyMuPDF
from streamlit_pdf_viewer import pdf_viewer
import sys
import os
from tika import parser

# 獲取當前文件的路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
# 將文件所在的目錄添加到 sys.path 中
sys.path.append(current_dir)
from page_layout import page_config
page_config()

TMP_DIR = Path(__file__).resolve().parent.joinpath('data', 'pdf')




from dataclasses import dataclass

# show the .pdf file in TMP_DIR without the suffix and the path
def show_pdf_files():
    pdf_files = [file.stem for file in TMP_DIR.iterdir() if file.suffix == '.pdf']
    return pdf_files


# add the streamlit selectbox to select the .pdf file in the sidebar
def select_pdf_file():
    pdf_files = show_pdf_files()
    pdf_file = st.sidebar.selectbox("filename", pdf_files)
    pdf_path = TMP_DIR / f"{pdf_file}.pdf"
    return pdf_path

# 加载文档
def load_documents():
    
    documents = []
    for pdf_file in TMP_DIR.glob('**/*.pdf'):
        documents.append(pdf_file)
    return documents


# show the selected .pdf file from TMP_DIR
def pdf_images(file_path):
    pdf_document = fitz.open(file_path)
    images = []
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        images.append(img)
    return images


# class PdfTransformer:
#     def __init__(self):
#         pass
#     def is_text_based_pdf(self, file_path):
#     """
#     Checks if a PDF file is text-based.

#     Parameters
#     ----------
#     file_path : str
#         The path of the PDF file to check.

#     Returns
#     -------
#     bool
#         True if the PDF contains text, False otherwise.
#     """
#     pdf_document = fitz.open(file_path)
#     for page_num in range(len(pdf_document)):
#         page = pdf_document[page_num]
#         if page.get_text("text").strip():
#             return True
#     return False

from pdf2image import convert_from_path

def ocr_pdf(file_path: str) -> str:
    """
    Uses OCR to extract text from an image-based PDF.

    Parameters
    ----------
    file_path : str
        The path of the PDF file to process with OCR.

    Returns
    -------
    str
        The extracted text content from the PDF.
    """
    images = convert_from_path(file_path)
    content = ''
    for image in images:
        text = pytesseract.image_to_string(image, lang='chi_tra')
        content += text
    
#     return content

# def load_documents(self, pdf_folder_path: str) -> dict:
#     """
#     Loads and processes all PDF files in the specified folder, returning their content.

#     Parameters
#     ----------
#     pdf_folder_path : str
#         The path of the folder containing PDF files.

#     Returns
#     -------
#     dict
#         A dictionary where the keys are file paths and the values are the extracted content.
#     """
#     pdf_fns = self.find_pdfs_in_folder(pdf_folder_path)
#     documents = {}
#     for pdf_fn in pdf_fns:
#         if self.is_text_based_pdf(pdf_fn):
#             raw = parser.from_file(pdf_fn)
#             content = raw['content']
#         else:
#             content = self.ocr_pdf(pdf_fn)
#         documents[pdf_fn] = content
#     return documents


# def read_pdf_file(pdf_file):
#     with open(TMP_DIR / f"{pdf_file}.pdf", "rb") as f:
#         pdf = f.read()
#     return pdf

st.markdown("# Comparison between original pdf and transformed text")


@dataclass
class TransformedText():
    '''
    Dataclass to store an image with its transformed text
    '''
    id: int
    fp: str
    # text = ""
    
    def __post_init__(self):
        pdf_document = fitz.open(self.fp)
        # images = {}
        # for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(self.id)
        pix = page.get_pixmap()
        self.img = Image.open(io.BytesIO(pix.tobytes()))
        
        # 
        istext_bool = page.get_text("text").strip()
        if istext_bool:
            raw = parser.from_file(self.fp)
            self.content = raw['content']
        else:
            self.content = ocr_pdf(self.fp)
            

        # images[page_num] = img
            
        # self.image = images[self.id]

if "pdf_images" not in st.session_state:
    pdf_file = select_pdf_file()
    images = pdf_images(pdf_file)
    st.session_state.images = images
else: 
    images = st.session_state.images

page_num = len(images)

def next(): st.session_state.counter += 1
def prev(): st.session_state.counter -= 1

if 'counter' not in st.session_state: st.session_state.counter = 0

if pdf_file is not None:
    st.write(pdf_file)
    pdf_document = fitz.open(pdf_file)
    page_num = pdf_document.page_count

    if "transformed" not in st.session_state:
        transformed_texts = []
        images = []
        for idx in range(page_num):
            page = pdf_document.load_page(idx)
            istext_bool = page.get_text("text").strip()
            st.write(istext_bool)
            if istext_bool:
                raw = parser.from_file(pdf_file)
                content = raw['content']
            else:
                content = ocr_pdf(pdf_file)
            transformed_texts.append(content)
            
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes()))
            images.append(img)
        
        st.session_state.transformed = transformed_texts
        st.session_state.images = images
    else:
        transformed_texts = st.session_state.transformed
        images = st.session_state.images

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("## Original PDF")
        cols = st.columns(2)
        with cols[1]: st.button("Next ➡️", on_click=next, use_container_width=True)
        with cols[0]: st.button("⬅️ Previous", on_click=prev, use_container_width=True)

        img = images[st.session_state.counter % page_num]
        st.image(img, use_column_width=True)

    with col2:
        st.markdown("## Transformed Text")
        transformed_text = transformed_texts[st.session_state.counter % page_num]
        st.write(transformed_text)
        


# col = st.columns((2, 2, 2), gap='medium')
# with col[0]:
#     st.markdown("# Doc comparison between origin & transformed text.")
#     st.sidebar.header("Select a PDF file")
#     st.write(
#         """This step illustrates a combination of plotting and animation with
#     Streamlit. We're generating a bunch of random numbers in a loop for around
#     5 seconds. Enjoy!"""
#     )
    
# with col[1]:
#     pdf_file = select_pdf_file()
#     # show the origin text
#     st.write("### Origin Text")
#     # show_pdf(pdf_file)
#     st.image(show_pdf(pdf_file))

# pdf_files = load_documents()

# if pdf_files:
#     pdf_file = pdf_files[0]  # 假设只有一个PDF文件

#     pdf_document = fitz.open(pdf_file)
#     total_pages = pdf_document.page_count

#     # 按钮导航
#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col1:
#         if st.button("上一页"):
#             if st.session_state.page > 0:
#                 st.session_state.page -= 1
#     with col3:
#         if st.button("下一页"):
#             if st.session_state.page < total_pages - 1:
#                 st.session_state.page += 1

#     current_page = st.session_state.page
#     st.write(f"当前页: {current_page + 1} / {total_pages}")

#     pdf_viewer(str(pdf_file), page_number=current_page + 1)
