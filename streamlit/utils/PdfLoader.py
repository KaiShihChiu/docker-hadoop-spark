
#%%
import os
import pytesseract
from pdf2image import convert_from_path
import fitz

class PdfLoader:
    """
    A class used to find and process PDF files in a given directory.

    Methods
    -------
    find_pdfs_in_folder(search_directory):
        Finds all PDF files in the specified directory and its subdirectories.

    is_text_based_pdf(file_path):
        Checks if a PDF file is text-based.

    ocr_pdf(file_path):
        Uses OCR to extract text from an image-based PDF.

    load_documents(pdf_folder_path):
        Loads and processes all PDF files in the specified folder, returning their content.
    """

    def __init__(self):
        pass

    def find_pdfs_in_folder(self, search_directory: str) -> list:
        """
        Finds all PDF files in the specified directory and its subdirectories.

        Parameters
        ----------
        search_directory : str
            The path of the directory to search for PDF files.

        Returns
        -------
        list
            A list of file paths for all found PDF files.
        """
        pdf_files = []

        for root, dirs, files in os.walk(search_directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        
        return pdf_files

    def is_text_based_pdf(self, file_path):
        """
        Checks if a PDF file is text-based.

        Parameters
        ----------
        file_path : str
            The path of the PDF file to check.

        Returns
        -------
        bool
            True if the PDF contains text, False otherwise.
        """
        pdf_document = fitz.open(file_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            if page.get_text("text").strip():
                return True
        return False

    def ocr_pdf(self, file_path: str) -> str:
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
        
        return content

    def load_documents(self, pdf_folder_path: str) -> dict:
        """
        Loads and processes all PDF files in the specified folder, returning their content.

        Parameters
        ----------
        pdf_folder_path : str
            The path of the folder containing PDF files.

        Returns
        -------
        dict
            A dictionary where the keys are file paths and the values are the extracted content.
        """
        pdf_fns = self.find_pdfs_in_folder(pdf_folder_path)
        documents = {}
        for pdf_fn in pdf_fns:
            if self.is_text_based_pdf(pdf_fn):
                raw = parser.from_file(pdf_fn)
                content = raw['content']
            else:
                content = self.ocr_pdf(pdf_fn)
            documents[pdf_fn] = content
        return documents