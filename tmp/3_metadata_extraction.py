# First, import the elements you need

from streamlit_elements import elements, mui, html
import streamlit as st
import numpy as np
import sys
import os
# 獲取當前文件的路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
# 將文件所在的目錄添加到 sys.path 中
sys.path.append(current_dir)
from page_layout import page_config
page_config()








#     # You can call any Streamlit command, including custom components:
#     # st.bar_chart(np.random.randn(50, 3))

# st.write("This is outside the container")

# with elements("dashboard"):
#     st.markdown(
#         """
#         <style>
#         .reportview-container .main .block-container {
#             padding-top: 1rem;
#             padding-bottom: 1rem;
#             padding-left: 5%;
#             padding-right: 5%;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )
#     # You can create a draggable and resizable dashboard using
#     # any element available in Streamlit Elements.

#     from streamlit_elements import dashboard

#     # First, build a default layout for every element you want to include in your dashboard

#     layout = [
#         # Parameters: element_identifier, x_pos, y_pos, width, height, [item properties...]
#         dashboard.Item("first_item", 0, 0, 80, 2, isDraggable=False, moved=False),
#         dashboard.Item("second_item", 2, 0, 80, 2, isDraggable=False, moved=False),
#     ]

#     # Next, create a dashboard layout using the 'with' syntax. It takes the layout
#     # as first parameter, plus additional properties you can find in the GitHub links below.

#     with dashboard.Grid(layout):
#         mui.Paper("First item", key="first_item")
#         mui.Paper("Second item", key="second_item")

#     # If you want to retrieve updated layout values as the user move or resize dashboard items,
#     # you can pass a callback to the onLayoutChange event parameter.

#     def handle_layout_change(updated_layout):
#         # You can save the layout in a file, or do anything you want with it.
#         # You can pass it back to dashboard.Grid() if you want to restore a saved layout.
#         print(updated_layout)

#     with dashboard.Grid(layout, onLayoutChange=handle_layout_change):
#         mui.Paper("First item", key="first_item")
#         mui.Paper("Second item (cannot drag)", key="second_item")
