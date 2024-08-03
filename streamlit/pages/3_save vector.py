import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))

import streamlit as st
from hivedb import HiveDB

# Initialize HiveDB
hive_db = HiveDB()

# Read gov_docs database
db = "gov_docs"

# Read content_table
content_table = 'content_table'
df_content = hive_db.read_table_into_df(content_table, db)

# Read metadata_table
metadata_table = 'metadata_table'
df_metadata = hive_db.read_table_into_df(metadata_table, db)

# Display the tables and the merged result
cols = st.columns(2)

with cols[0]:
    st.subheader("Content Table")
    st.write(df_content.columns)
    st.write(df_content)

with cols[1]:
    st.subheader("Metadata Table")
    st.write(df_metadata.columns)
    st.write(df_metadata)

# Ensure unique values in metadata_table.filename
df_metadata_unique = df_metadata.drop_duplicates(subset=['metadata_table.filename'])

# Merge the two tables based on the filename
df_merged = df_content.merge(df_metadata_unique, how='left', left_on='content_table.filename', right_on='metadata_table.filename')

# Select and rename the columns as needed
df_merged = df_merged[['content_table.filename', 'content_table.cleaned', 'metadata_table.keywords']]

st.subheader("Merged Table")
st.write(df_merged)


from langchain_chroma import Chroma
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document

