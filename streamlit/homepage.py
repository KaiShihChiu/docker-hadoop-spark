import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
    layout="wide"
)

st.write("# Welcome to HRrag pipline! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    HRrag pipline is an app framework built specifically for
    RAG projects that visulize every steps needed.
    **👈 Select a demo from the sidebar** to see basic steps of building RAG!
    ### Steps:
    - **Document loading**: PDF, Word, Image (png and jpeg etc.)
    - **Data cleaning**: different data may need different cleaning methods, but the important thing is to make sure the explanation part is extracted.
    - **MetaData extraction**: 
    - **Vectorization**: 
    - **Querying**: 
    - **Retireval**: 
    - **Prompting**: 
    - **Answering**: 
"""
)


# print("Hello")


