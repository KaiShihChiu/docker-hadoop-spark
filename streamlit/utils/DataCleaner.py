
import re

class DataCleaner:
    """
    A class used to clean text data.

    Methods
    -------
    extract_explanation(text):
        Extracts the explanation part from the text.

    remove_binding_lines_and_dots(text):
        Removes "裝訂線" and surrounding dots and spaces from the text.

    remove_page_numbers(text):
        Removes page numbers formatted as "第X頁、共X頁" or "第X頁/*-共X頁" from the text.

    remove_crosspage_char(text):
        Removes cross-page characters from the text.

    remove_irregular_characters(text):
        Removes irregular characters from the text.

    remove_blank(text):
        Removes extra spaces between characters in the text.

    data_check(text):
        Checks if the text contains the keywords "說明" and "正本".

    clean_wo_keywords(text):
        Cleans the text without the keywords "說明" and "正本".

    data_cleaning(text):
        Cleans the text based on certain conditions.
    """

    def __init__(self):
        pass

    def extract_explanation(self, text: str) -> str:
        """
        Extracts the explanation part from the text.

        Parameters
        ----------
        text : str
            The input text from which to extract the explanation.

        Returns
        -------
        str
            The extracted explanation, or an empty string if not found.
        """
        pattern = re.compile(r'(?:\s|。)說\s*明\s*[:：。，；]*\s*(.*?)\s*正\s*本', re.DOTALL)
        match = pattern.search(text)
        if match:
            text = match.group(1)
        
        pattern = re.compile(r'速別\s*[:：。，；]*\s*(.*?)\s*正本', re.DOTALL)
        match = pattern.search(text)
        if match:
            text = match.group(1)
        
        pattern = re.compile(r'(?:\s|。)說\s*明\s*[:：。，；]*\s*(.*)', re.DOTALL)
        match = pattern.search(text)
        if match:
            text = match.group(1)
        
        return text
            
            
            


    def remove_binding_lines_and_dots(self, text: str) -> str:
        """
        Removes "裝訂線" and surrounding dots and spaces from the text.

        Parameters
        ----------
        text : str
            The input text from which to remove the binding lines and dots.

        Returns
        -------
        str
            The cleaned text.
        """
        pattern_binding_line = re.compile(r'(\s*\.\s*)*裝(\s*\.\s*)*訂(\s*\.\s*)*線(\s*\.\s*)*', re.DOTALL)
        text = re.sub(pattern_binding_line, '', text)
        
        pattern_dots = re.compile(r'\s*\.\s*')
        text = re.sub(pattern_dots, '', text)
        return text

    def remove_page_numbers(self, text: str) -> str:
        """
        Removes page numbers formatted as "第X頁、共X頁" or "第X頁/*-共X頁" from the text.

        Parameters
        ----------
        text : str
            The input text from which to remove the page numbers.

        Returns
        -------
        str
            The cleaned text.
        """
        pattern_page_numbers = re.compile(r'第\s*\d+\s*頁\s*，\s*共\s*\d+\s*頁')
        text = re.sub(pattern_page_numbers, '', text)
        
        pattern = r"第\d+頁 共\d+."
        text = re.sub(pattern, '', text).strip()
        
        pattern = r"第\d+頁[^\u4e00-\u9fa5]*共\d+頁"
        text = re.sub(pattern, '', text).strip()
        
        return text

    def remove_crosspage_char(self, text: str) -> str:
        """
        Removes cross-page characters from the text.

        Parameters
        ----------
        text : str
            The input text from which to remove cross-page characters.

        Returns
        -------
        str
            The cleaned text.
        """
        # pattern = re.compile(r'檔\s*　*\s*號.*?共\d+頁', re.DOTALL)
        # # 替换匹配的内容为空字符串
        # text = pattern.sub('', text)
        pattern = r'檔\s*　*\s*號.*?第 \d 頁，共 \d 頁'
        text = re.sub(pattern, '', text, flags=re.DOTALL)
        return text

    def remove_irregular_characters(self, text: str) -> str:
        """
        Removes irregular characters from the text.

        Parameters
        ----------
        text : str
            The input text from which to remove irregular characters.

        Returns
        -------
        str
            The cleaned text.
        """
        pattern = r'\d[^\u4e00-\u9fa5a-zA-Z0-9]+'
        cleaned_text = re.sub(pattern, '', text)
        pattern = r'。\d+'
        cleaned_text = re.sub(pattern, '。', cleaned_text)
        pattern = r"\|\s*"
        cleaned_text = re.sub(pattern, '', cleaned_text)
        pattern = r"(?<=。)[a-zA-Z]+"
        cleaned_text = re.sub(pattern, '', cleaned_text)
        return cleaned_text

    def remove_blank(self, text: str) -> str:
        """
        Removes extra spaces between characters in the text.

        Parameters
        ----------
        text : str
            The input text from which to remove extra spaces.

        Returns
        -------
        str
            The cleaned text.
        """
        pattern = r"(?<=\S)\s+(?=\S)"
        cleaned_text = re.sub(pattern, ' ', text)
        return cleaned_text

    def data_check(self, text: str) -> str:
        """
        Checks if the text contains the keywords "說明" and "正本".

        Parameters
        ----------
        text : str
            The input text to check for keywords.

        Returns
        -------
        bool
            True if both keywords are found, False otherwise.
        """
        if "說明" in text and "正本" in text:
            return True
        return False

    def clean_wo_keywords(self, text: str) -> str:
        """
        Cleans the text without the keywords "說明" and "正本".

        Parameters
        ----------
        text : str
            The input text to clean.

        Returns
        -------
        str
            The cleaned text.
        """
        pattern = r"速別:[\s\S]*?\n\s*\n\s*([\s\S]*?)(?=\n\n正本)"
        match = re.search(pattern, text)
        if match:
            result = match.group(1).strip()
            return result
        else:
            return ""

    def data_cleaning(self, text: str) -> str:
        """
        Cleans the text based on certain conditions.

        Parameters
        ----------
        text : str
            The input text to clean.

        Returns
        -------
        str
            The fully cleaned text.
        """
        # if self.data_check(text):
        number_removed = self.remove_crosspage_char(text)
        explnation = self.extract_explanation(number_removed)
        text_explain = explnation.replace("\n", "")
        cleaned_line = self.remove_binding_lines_and_dots(text_explain)
        cleaned_pagenumber = self.remove_page_numbers(cleaned_line)
        cleaned_char = self.remove_irregular_characters(cleaned_pagenumber)
        cleaned = self.remove_blank(cleaned_char)
        # elif "正本" in text:
        #     cleaned_wo_keyword = self.clean_wo_keywords(text)
        #     cleaned_pagenumber = self.remove_page_numbers(cleaned_wo_keyword)
        #     cleaned_line = cleaned_pagenumber.replace("\n", "")
        #     cleaned = self.remove_blank(cleaned_line)
        # else:
        #     cleaned_line = text.replace("\n", "")
        #     cleaned = self.remove_blank(cleaned_line)

        return cleaned

#%%

if __name__ == "__main__":
    # read the text from the file
    file_path = 'test.txt'
    with open(file_path, 'r') as file:
        text = file.read()
    
    # create an instance of the DataCleaner class
    data_cleaner = DataCleaner()
    # pattern = re.compile(r'說\s*明\s*[:：。，；]*\s*(.*?)\s*正\s*本', re.DOTALL)

    # match = pattern.search(text)
    # cleaned = match.group(1)
    cleaned = data_cleaner.data_cleaning(text)
    
    print(cleaned)