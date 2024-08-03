from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from DataCleaner import DataCleaner
from dotenv import load_dotenv
load_dotenv()

data_cleaner = DataCleaner()

# Function to read text file
def read_txt(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data


api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise ValueError("Did not find groq_api_key, please add an environment variable `GROQ_API_KEY` which contains it, or pass `groq_api_key` as a named parameter.")

# Function to improve text using groq and prompt
def improve_text(text):
    llm = ChatGroq(
        model="llama3-70b-8192",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=api_key
        # other params...
    )
    
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "下列文章有諸多語意錯誤、標點符號問題、或是影響語意流暢度的錯別字等影響閱讀的內容，請依據撰寫公文的專業人員的角度進行排版以及一些文字的修正，修正的數目越少越好，不要偏離主要意思。\
                 排版要依序為 一、 二、... (一) (二) ... 1. 2. 3.  ...   \
                請務必使用繁體中文回答，且只回答需要的部分，無須給予其他非相關的文字。",
            ),
            ("human", "{text}"),
        ]
    )
    
    chain = prompt | llm
    response = chain.invoke(
                    {
                        "text": text,
                    }
                )
    
    improved_text = response.content
    return improved_text



if __name__ == '__main__':
# Read text from file
    file_path = 'test.txt'
    text = read_txt(file_path)
    
    explanation = data_cleaner.extract_explanation(text)
    # print(explanation)

    # Improve the text
    improved_text = improve_text(explanation)
    print(improved_text)

# Print the improved text
# print(improved_text)
