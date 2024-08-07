import streamlit as st
import pandas as pd
from datetime import datetime
import random
import asyncio
import semantic_kernel as sk

from pathlib import Path
import os
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
import json

import sys
current_path = Path(__file__).resolve()
parent_path = current_path.parent.parent
sys.path.append(str(parent_path))


from src.utils import extract_parameters
from src.agents_sk import ResearchTools










def save_email(email):
    # Implement email saving functionality here
    return True

def upload_material(file):
    # Implement material upload and RAG functionality here
    return True

# Set page config
st.set_page_config(page_title="Duke AI Scholar Paper Retrieval", layout="wide")

# Custom CSS (updated for button style and keyword box)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Open Sans', sans-serif;
    }
    .main {
        background-color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        background-color: #012169;
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
        transition-duration: 0.4s;
    }
    .stButton>button:hover {
        background-color: #001a4c;
    }
    .paper-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 5px;
        border-left: 5px solid #012169;
        margin-bottom: 20px;
    }
    .css-1aumxhk {
        background-color: #e8eef7;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #012169;
    }
    .stAlert {
        background-color: #c9d8ef;
        color: #012169;
    }
    .stDataFrame {
        border: 1px solid #012169;
    }
    .streamlit-expanderHeader {
        background-color: #012169;
        color: white !important;
        border-radius: 5px;
        padding: 10px !important;
        font-weight: bold !important;
    }
    .streamlit-expanderContent {
        background-color: #e8eef7;
        border: 1px solid #012169;
        border-top: none;
        border-radius: 0 0 5px 5px;
        padding: 10px;
    }
    .keyword-chip {
        display: inline-block;
        background-color: #e8eef7;
        color: #012169;
        padding: 5px 10px;
        margin: 2px;
        border-radius: 15px;
        font-size: 0.9em;
    }
    .keyword-container {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-bottom: 10px;
        background-color: #f8f9fa;
        border: 1px solid #012169;
        border-radius: 5px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("🎓 Duke AI Scholar Paper Retrieval")
st.markdown("---")

# Main content
col1, col2 = st.columns([2, 1])

# Set up your session state for keywords if not already initialized
if 'keywords' not in st.session_state:
    st.session_state.keywords = []
with col1:
    st.subheader("Enter Keywords")

    # Text input for keywords
    keyword_input = st.text_input("Enter a keyword and press Enter (add multiple keywords one by one):", key="keyword_input")

    # Create a row with two columns for the buttons
    col_add, col_clear = st.columns(2)

    with col_add:
        # Button to add keywords
        if st.button("Add Keyword"):
            if keyword_input:
                # Check to avoid adding empty or duplicate keywords
                if keyword_input not in st.session_state.keywords:
                    st.session_state.keywords.append(keyword_input)
                # Trigger a rerun to clear the text input
                st.rerun()

    with col_clear:
        # Button to clear all keywords
        if st.button("Clear Keywords"):
            st.session_state.keywords = []
            # This also triggers a rerun to reset the app state including the text input
            st.rerun()

    # Displaying the keywords
    if st.session_state.keywords:
        st.write("Entered keywords:")
        st.markdown('<div class="keyword-container">' +
                    ''.join([f'<span class="keyword-chip">{keyword}</span>' for keyword in st.session_state.keywords]) +
                    '</div>', unsafe_allow_html=True)

    st.subheader("Search for Papers")
    
    
    query = st.text_input("Enter your search query:")
    if st.button("Search", key="search_button"):
        if 'keywords' in st.session_state and st.session_state.keywords:
            
            async def retrieve_paper():
                # Initialize the kernel
                kernel = sk.Kernel()
                table_column = st.session_state.keywords
                # Create ResearchTools instance
                research_tools = ResearchTools()
                kernel.add_plugin(research_tools, plugin_name="research_tools")
                research_tools.setup_llm(kernel)
                research_tools.setup_info_extractor(table_column)
                
                
                #Extract keywords
                keywords = await kernel.invoke(
                    function_name="get_keywords",
                    plugin_name="research_tools", 
                    kernel = kernel, query=query)
                results = str(keywords.value[0])
                params = extract_parameters(results)
                
                
                #Save reuslts to dataframe
                keywords = await kernel.invoke(
                    function_name="retrieve_papers",
                    plugin_name="research_tools", 
                    num_papers = 1,
                    **params)
                return keywords
            
            results = asyncio.run(retrieve_paper()).value
            
            # print("----------------------------")
            # print(results)
            # print("----------------------------")
            # # Convert the list of dictionaries to a pandas DataFrame
            df = pd.DataFrame(results)

            print("----------------------------")
            print(df)
            print("----------------------------")
            
            
            # Display the DataFrame
            st.dataframe(df)

            # If you want to allow expanding each row for more details:
            for i, paper in enumerate(results):
                with st.expander(f"Details for paper {i+1}: {paper['title']}"):
                    for key, value in paper.items():
                        st.markdown(f"**{key}:** {value}")
            # # Display results
            # for paper in results:
            #     with st.expander(f"**{paper['title']}** ({paper['year']})"):
            #         st.markdown(f"<div class='paper-box'><strong>Authors:</strong> {paper['authors']}<br><strong>Abstract:</strong> {paper['abstract']}</div>", unsafe_allow_html=True)
            
            # Save query to history
            if 'history' not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append((datetime.now(), query, ', '.join(st.session_state.keywords)))
        else:
            st.warning("Please enter at least one keyword before searching.")

with col2:
    with st.expander("📧 Subscribe for Updates", expanded=True):
        st.subheader("Get Regular Paper Updates")
        email = st.text_input("Enter your email address:")
        if st.button("Subscribe", key="subscribe_button"):
            if save_email(email):
                st.success("You've been subscribed for regular paper updates!")
            else:
                st.error("There was an error subscribing. Please try again.")
    
    with st.expander("📁 Upload Reference Material", expanded=True):
        st.subheader("Enhance Our Knowledge Base")
        uploaded_file = st.file_uploader("Choose a file to upload:")
        if uploaded_file is not None:
            if upload_material(uploaded_file):
                st.success("Material uploaded successfully!")
            else:
                st.error("There was an error uploading the file. Please try again.")

# Query History
st.markdown("---")
st.subheader("📜 Query History")
if 'history' in st.session_state and st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history, columns=["Timestamp", "Query", "Keywords"])
    history_df = history_df.sort_values("Timestamp", ascending=False).reset_index(drop=True)
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No search history available yet. Start searching to see your history!")

# Footer
st.markdown("---")
st.markdown("© 2024 Duke University AI Scholar Paper Retrieval | Built with ❤️ using Streamlit")
