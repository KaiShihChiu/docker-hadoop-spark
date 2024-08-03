import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))

import streamlit as st
from hivedb import HiveDB

# Initialize HiveDB
hive_db = HiveDB()

# Initialize session state for tracking selected database, table, and table list
if 'selected_db' not in st.session_state:
    st.session_state.selected_db = None
if 'selected_table' not in st.session_state:
    st.session_state.selected_table = None
if 'tables' not in st.session_state:
    st.session_state.tables = ['Select a database first']
if 'show_confirm' not in st.session_state:
    st.session_state.show_confirm = False
    
# Fetch and display databases
databases = hive_db.show_databases()
databases = ['Please select a database'] + databases
select_db = st.sidebar.selectbox("Select the database", databases)

# Check if the selected database has changed
if select_db != 'Please select a database' and select_db != st.session_state.selected_db:
    st.session_state.selected_db = select_db

    # Use the selected database
    hive_db.use_database(select_db)
    tables = hive_db.show_tables()
    st.session_state.tables = ['Please select a table'] + tables  # Reset table selection when database changes

# Fetch and display tables in the selected database
select_tb = st.sidebar.selectbox("Select the table", st.session_state.tables)


confirm_button = st.sidebar.button("Confirm", key= 'confirm_button', disabled=(select_db == 'Please select a database' or select_tb == 'Please select a table'))
delete_button = st.sidebar.button("Delete", key = 'delete_button', disabled=(select_tb == 'Please select a table'))


if confirm_button:
    st.write(f"Selected Database: {select_db}")
    st.write(f"Selected Table: {select_tb}")
    
    # Fetch and display the table data
    df = hive_db.read_table_into_df(select_tb, select_db)
    st.write(df)


if delete_button:
    st.session_state.show_confirm = True

# Show confirmation dialog if delete button is clicked
if st.session_state.show_confirm:
    st.sidebar.write("Are you sure you want to delete this table?")
    confirm_delete = st.sidebar.button("Yes, delete")
    cancel_delete = st.sidebar.button("Cancel")

    if confirm_delete:
        # Your delete logic here
        hive_db.delete_table(select_tb, select_db)
        st.write(f"Table {select_tb} in database {select_db} has been deleted.")
        st.session_state.show_confirm = False
        hive_db.use_database(select_db)
        tables = hive_db.show_tables()
        st.session_state.tables = ['Please select a table'] + tables  # Reset table selection when database changes

    if cancel_delete:
        st.session_state.show_confirm = False