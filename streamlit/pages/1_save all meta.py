
from hivedb import HiveDB
import streamlit as st
import pandas as pd

if st.button('Start Progress'):
    with st.spinner('Data loading...'):

        hive_db = HiveDB()
        db = "gov_docs"
        hive_db.use_database(db)
        databases = hive_db.show_databases()

        table_name = 'content_table'
        df_content = hive_db.read_table_into_df(table_name)
        st.header("Content Table")
        st.write(df_content)
        
        # add data loading progress bar
    
    st.success('Data loaded successfully!')
    
    with st.spinner('Extracting and saving metadata...'):
        # create a new table for the metadata
        metadata_table = 'metadata_table'
        metadata_columns = {
            'filename': 'STRING',
            'keywords': 'STRING'
        }
        
        from MetaDataExtractor import MetaDataExtractor
        meta_extractor = MetaDataExtractor()
        df_metadata = meta_extractor.extract_metadata(df_content)

        st.header("Metadata Table")
        st.write(df_metadata)
        meta_table = 'metadata_table'
        
        # save the metadata to the database
        hive_db.insert_data_from_df(meta_table, df_metadata)

    st.success('Metadata saved successfully!')