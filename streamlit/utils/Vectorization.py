

from hivedb import HiveDB
# setup Chroma in-memory, for easy prototyping. Can add persistence easily!
client = chromadb.Client()

hive_db = HiveDB()
db = 'test'

hive_db.use_database(db)

tbs = hive_db.show_tables()
print(tbs)

tb = 'testdf2_table'

df = hive_db.read_table_into_df(tb)

print(df)


from langchain_core.documents import Document

# turn the dataframe into a list of documents with metadata
documents = []
for i in range(len(df)):
    document = Document(
        page_content=df.iloc[i]['content'],
        metadata={
            'filename': df.iloc[i]['filename'],
            'style': df.iloc[i]['style']
        }
    )
    documents.append(document)















# import
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import CharacterTextSplitter








documents = 

# split it into chunks
text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

# create the open-source embedding function
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# load it into Chroma
db = Chroma.from_documents(docs, embedding_function)

# query it
query = "What did the president say about Ketanji Brown Jackson"
docs = db.similarity_search(query)

# print results
print(docs[0].page_content)