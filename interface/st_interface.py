import sys
import streamlit as st
import pandas as pd
from datetime import datetime
import asyncio
import semantic_kernel as sk
from pathlib import Path

# Ensure the necessary local directories are accessible
current_path = Path(__file__).resolve()
parent_path = current_path.parent.parent
sys.path.append(str(parent_path))

from src.utils import extract_parameters
from src.agents_sk import ResearchTools


def save_email(email):
    # Placeholder for email saving functionality
    return True


def upload_material(file):
    # Placeholder for material upload functionality
    return True


def get_available_models():
    # Returns a list of available models; extend this as more models become available
    return ["LLaMA-3", "LLaMA-2", "Mistral", "Gemma", "GPT-4", "GPT-3.5 Turbo"]


def upload_to_zotero(user_id, api_key, papers):
    # Placeholder for Zotero upload functionality
    # Replace with actual implementation and return True if successful, False otherwise
    return True


# Configure the Streamlit page
st.set_page_config(page_title="🛸SciOptimizer", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Open Sans', sans-serif;
    }
    .main {
        background-color: #ffffff;
    }
    .stButton > button {
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
    .stButton > button:hover {
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
""",
    unsafe_allow_html=True,
)

# Header setup
st.title("🛸SciOptimizer")
st.markdown("---")

# Main content layout
col1, col2 = st.columns([2, 1])

# Initialize session state for keywords
if "keywords" not in st.session_state:
    st.session_state.keywords = []

with col1:
    st.subheader("✏️ Specify Table Columns")

    # Input for keywords
    keyword_input = st.text_input(
        "Enter each keyword you want to extract from the paper and press Enter after each one: ",
        key="keyword_input",
    )

    # Row with two columns for buttons
    col_add, col_clear = st.columns(2)

    with col_add:
        # Button to add keywords
        if st.button("Add Keyword"):
            if keyword_input and keyword_input not in st.session_state.keywords:
                st.session_state.keywords.append(keyword_input)
                st.rerun()

    with col_clear:
        # Button to clear all keywords
        if st.button("Clear Keywords"):
            st.session_state.keywords = []
            st.rerun()

    # Displaying keywords
    if st.session_state.keywords:
        st.write("Entered keywords:")
        st.markdown(
            '<div class="keyword-container">'
            + "".join(
                [
                    f'<span class="keyword-chip">{keyword}</span>'
                    for keyword in st.session_state.keywords
                ]
            )
            + "</div>",
            unsafe_allow_html=True,
        )

    st.subheader("🎯 Search for Papers")

    col_query, col_num_papers = st.columns([3, 1])
    with col_query:
        query = st.text_input("Enter your search query:")
    with col_num_papers:
        num_papers = st.number_input(
            "Number of papers", min_value=1, max_value=10, value=1, step=1
        )

    if st.button("Search", key="search_button"):
        if "keywords" in st.session_state and st.session_state.keywords:

            async def retrieve_paper():
                kernel = sk.Kernel()
                table_column = st.session_state.keywords

                research_tools = ResearchTools(
                    kernel=kernel, model=st.session_state.selected_model
                )
                kernel.add_plugin(research_tools, plugin_name="research_tools")

                if "api_key" not in st.session_state:
                    api_key = None
                else:
                    api_key = st.session_state.api_key
                research_tools.setup_llm(api_key=api_key)
                research_tools.setup_info_extractor(table_column)

                keywords = await kernel.invoke(
                    function_name="get_keywords",
                    plugin_name="research_tools",
                    kernel=kernel,
                    query=query,
                )
                results = str(keywords.value[0])

                print(results)
                params = extract_parameters(results)

                papers = await kernel.invoke(
                    function_name="retrieve_papers",
                    plugin_name="research_tools",
                    num_papers=num_papers,
                    **params,
                )
                return papers

            results = asyncio.run(retrieve_paper()).value
            df = pd.DataFrame(results)
            st.dataframe(df)

            for i, paper in enumerate(results):
                with st.expander(f"Details for **{paper['title']}**"):
                    for key, value in paper.items():
                        st.markdown(f"**{key}:** {value}")

            if "history" not in st.session_state:
                st.session_state.history = []
            if "query_results" not in st.session_state:
                st.session_state.query_results = []
            st.session_state.history.append(
                (
                    datetime.now(),
                    query,
                    ", ".join(st.session_state.keywords),
                    num_papers,
                )
            )
            st.session_state.query_results.append(df)
        else:
            st.warning("Please enter at least one keyword before searching.")

with col2:
    # Ensure that the selected model is remembered across sessions
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None

    with st.expander("🤖 Select AI Model", expanded=True):
        st.subheader("Choose AI Model")
        available_models = get_available_models()

        # The selected_model is now directly tied to the session_state, ensuring its persistence
        st.session_state.selected_model = st.selectbox(
            "Select an AI model for paper retrieval:",
            available_models,
            index=(
                available_models.index(st.session_state.selected_model)
                if st.session_state.selected_model in available_models
                else 0
            ),
            key="model_selector",  # Changed key to avoid conflict
        )
        st.info(f"Current model: {st.session_state.selected_model}")

        if st.session_state.selected_model in ["GPT-4", "GPT-3.5 Turbo"]:
            if "api_key" not in st.session_state:
                st.session_state.api_key = None

            api_key_input = st.text_input(
                "Enter your OpenAI API key:",
                type="password",
                value=st.session_state.api_key,
                key="api_key_input",
            )

            def update_api_key():
                st.session_state.api_key = api_key_input  # Update the API key in a callback to avoid premature state locking

            st.button("Set API Key", on_click=update_api_key)

            if api_key_input:
                st.success("API key set successfully!")
            else:
                st.warning("Please enter your API key for ChatGPT models.")

    with st.expander("📖 Upload to Zotero", expanded=True):
        st.subheader("Add Papers to Zotero")
        zotero_user_id = st.text_input("Enter your Zotero User ID:")
        zotero_api_key = st.text_input("Enter your Zotero API key:", type="password")

        if st.button("Upload to Zotero", key="zotero_upload_button"):
            if "history" in st.session_state and st.session_state.history:
                if zotero_user_id and zotero_api_key:
                    last_search_results = st.session_state.query_results[-1]
                    papers = [
                        row.to_dict() for index, row in last_search_results.iterrows()
                    ]

                async def add_to_zotero():
                    kernel = sk.Kernel()
                    research_tools = ResearchTools(
                        kernel=kernel, model=st.session_state.selected_model
                    )
                    kernel.add_plugin(research_tools, plugin_name="research_tools")
                    success = await kernel.invoke(
                        function_name="save_to_zotero",
                        plugin_name="research_tools",
                        papers=papers,
                        LIBRARY_TYPE="user",
                        USER_ID=zotero_user_id,
                        API_KEY=zotero_api_key,
                    )
                    return success

                results = asyncio.run(add_to_zotero()).value

                if results:
                    st.success("Papers successfully uploaded to Zotero!")
                else:
                    st.error(
                        "There was an error uploading papers to Zotero. Please try again."
                    )
            else:
                st.warning("Please enter both Zotero User ID and API key.")

# Query History
st.markdown("---")
st.subheader("📜 Query History")
if "history" in st.session_state and st.session_state.history:
    history_df = pd.DataFrame(
        st.session_state.history,
        columns=["Timestamp", "Query", "Keywords", "Number of Papers"],
    )
    history_df = history_df.sort_values("Timestamp", ascending=False).reset_index(
        drop=True
    )
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No search history available yet. Start searching to see your history!")

# Footer
st.markdown("---")
