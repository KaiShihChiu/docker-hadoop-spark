
from langchain_core.documents import Document
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from langchain_community.document_loaders import DirectoryLoader
from tika import parser
import spacy
import os 
import re
import pandas as pd

TOKENIZERS_PARALLELISM=True
# 加載 spaCy 模型
nlp = spacy.load("zh_core_web_sm")

class MetaDataExtractor:
    """
    A class used to extract metadata from text data.

    Methods
    -------
    extract_issue_date(text):
        Extracts the issue date from the text.

    extract_issue_number(text):
        Extracts the issue number from the text.

    extract_subject(text):
        Extracts the subject from the text.

    extract_keywords(text):
        Extracts keywords from the text using jieba and TF-IDF.

    extract_metadata(file_path, content):
        Extracts various metadata from the text and returns them as a dictionary.
    """

    def __init__(self):
        # 定義繁體中文停用詞列表
        self.chinese_stopwords = set([
                    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一個', '上', '也', '很', '到', '說', '要', '去',
                    '你', '會', '著', '沒有', '看', '好', '自己', '這', '有關', '那', '問題', '不是', '這個', '不會', '不要', '他', '來',
                ])

    # def extract_issue_date(self, text: str) -> str:
    #     """
    #     Extracts the issue date from the text.

    #     Parameters
    #     ----------
    #     text : str
    #         The input text from which to extract the issue date.

    #     Returns
    #     -------
    #     str
    #         The extracted issue date, or an empty string if not found.
    #     """
    #     match = re.search(r'發文日期：([中華民國]*\d+年\d+月\d+日)', text)
    #     if match:
    #         return match.group(1).strip()
    #     return ""

    # def extract_issue_number(self, text: str) -> str:
    #     """
    #     Extracts the issue number from the text.

    #     Parameters
    #     ----------
    #     text : str
    #         The input text from which to extract the issue number.

    #     Returns
    #     -------
    #     str
    #         The extracted issue number, or an empty string if not found.
    #     """
    #     match = re.search(r'發文字號：(.*)', text)
    #     if match:
    #         return match.group(1).strip()
    #     return ""

    # def extract_subject(self, text: str) -> str:
    #     """
    #     Extracts the subject from the text.

    #     Parameters
    #     ----------
    #     text : str
    #         The input text from which to extract the subject.

    #     Returns
    #     -------
    #     str
    #         The extracted subject, or an empty string if not found.
    #     """
    #     pattern = r'主旨:(.*?)說明:'
    #     match = re.search(pattern, text, re.DOTALL)
    #     if match:
    #         return match.group(1).strip()
    #     return ""

    def extract_keywords(self, text: str) -> str:
        """
        Extracts keywords from the text using jieba and TF-IDF.

        Parameters
        ----------
        text : str
            The input text from which to extract keywords.

        Returns
        -------
        list
            A list of extracted keywords.
        """
        # 使用 jieba 進行繁體中文分詞
        
        words = jieba.lcut(text)
        words = [word for word in words if word not in self.chinese_stopwords and len(word) > 1]
        
        # 使用 TF-IDF 過濾關鍵詞
        vectorizer = TfidfVectorizer(max_features=15)
        tfidf_matrix = vectorizer.fit_transform([" ".join(words)])
        keywords = vectorizer.get_feature_names_out()
        return keywords

    def extract_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts various metadata from the text and returns them as a DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            A DataFrame with columns "filename" and "content".

        Returns
        -------
        pd.DataFrame
            A DataFrame containing extracted metadata: filename, keywords.
        """
        def extract_row_metadata(row):
            filename = row['content_table.filename']
            cleaned = row['content_table.cleaned']
            return {
                'filename': filename,
                'keywords': self.extract_keywords(cleaned),
                # 'date': self.extract_issue_date(content),
                # 'number': self.extract_issue_number(content),
                # 'subject': self.extract_subject(content)
            }

        metadata_df = df.apply(extract_row_metadata, axis=1, result_type='expand')
        return metadata_df