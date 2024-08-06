
import streamlit as st
import pandas as pd
from datetime import datetime
import random

# Placeholder functions (you'll need to implement these)
def search_papers(query):
    # Implement your AI agent's paper search functionality here
    return [{"title": f"Sample Paper about {query}", "authors": f"Author {random.randint(1,5)}, Author {random.randint(6,10)}", "year": random.randint(2020, 2024), "abstract": f"This is a sample abstract about {query}..."}
            for _ in range(1)]

def save_email(email):
    # Implement email saving functionality here
    return True

def upload_material(file):
    # Implement material upload and RAG functionality here
    return True

# Set page config
st.set_page_config(page_title="Duke AI Scholar Paper Retrieval", layout="wide")

# Custom CSS
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
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("🎓 Duke AI Scholar Paper Retrieval")
st.markdown("---")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Search for Papers")
    query = st.text_input("Enter your search query:")
    if st.button("Search", key="search_button"):
        results = search_papers(query)
        
        # Display results
        for paper in results:
            with st.expander(f"**{paper['title']}** ({paper['year']})"):
                st.markdown(f"<div class='paper-box'><strong>Authors:</strong> {paper['authors']}<br><strong>Abstract:</strong> {paper['abstract']}</div>", unsafe_allow_html=True)
        
        # Save query to history
        if 'history' not in st.session_state:
            st.session_state.history = []
        st.session_state.history.append((datetime.now(), query))

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
    history_df = pd.DataFrame(st.session_state.history, columns=["Timestamp", "Query"])
    history_df = history_df.sort_values("Timestamp", ascending=False).reset_index(drop=True)
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No search history available yet. Start searching to see your history!")

# Footer
st.markdown("---")
st.markdown("© 2024 Duke University AI Scholar Paper Retrieval | Built with ❤️ using Streamlit")


#  import streamlit as st
# import pandas as pd
# from datetime import datetime
# import random

# # Placeholder functions (you'll need to implement these)
# def search_papers(query):
#     # Implement your AI agent's paper search functionality here
#     return [{"title": f"Sample Paper about {query}", "authors": f"Author {random.randint(1,5)}, Author {random.randint(6,10)}", "year": random.randint(2020, 2024), "abstract": f"This is a sample abstract about {query}..."}
#             for _ in range(5)]

# def save_email(email):
#     # Implement email saving functionality here
#     return True

# def upload_material(file):
#     # Implement material upload and RAG functionality here
#     return True

# # Set page config
# st.set_page_config(page_title="Duke AI Scholar Paper Retrieval", layout="wide")

# # Custom CSS
# st.markdown("""
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap');
    
#     html, body, [class*="css"] {
#         font-family: 'Open Sans', sans-serif;
#     }
#     .main {
#         background-color: #ffffff;
#     }
#     .stButton>button {
#         width: 100%;
#         background-color: #012169;
#         color: white;
#     }
#     .stButton>button:hover {
#         background-color: #001a4c;
#     }
#     .paper-box {
#         background-color: #f8f9fa;
#         padding: 20px;
#         border-radius: 5px;
#         border-left: 5px solid #012169;
#         margin-bottom: 20px;
#     }
#     .css-1aumxhk {
#         background-color: #e8eef7;
#         border-radius: 10px;
#         padding: 20px;
#         margin-bottom: 20px;
#     }
#     h1, h2, h3 {
#         color: #012169;
#     }
#     .stAlert {
#         background-color: #c9d8ef;
#         color: #012169;
#     }
#     .stDataFrame {
#         border: 1px solid #012169;
#     }
#     </style>
#     """, unsafe_allow_html=True)

# # Header
# st.title("🎓 Duke AI Scholar Paper Retrieval")
# st.markdown("---")

# # Main content
# col1, col2 = st.columns([2, 1])

# with col1:
#     st.subheader("Search for Papers")
#     query = st.text_input("Enter your search query:")
#     if st.button("Search", key="search_button"):
#         results = search_papers(query)
        
#         # Display results
#         for paper in results:
#             with st.expander(f"**{paper['title']}** ({paper['year']})"):
#                 st.markdown(f"<div class='paper-box'><strong>Authors:</strong> {paper['authors']}<br><strong>Abstract:</strong> {paper['abstract']}</div>", unsafe_allow_html=True)
        
#         # Save query to history
#         if 'history' not in st.session_state:
#             st.session_state.history = []
#         st.session_state.history.append((datetime.now(), query))

# with col2:
#     with st.expander("📧 Subscribe for Updates", expanded=True):
#         st.subheader("Get Regular Paper Updates")
#         email = st.text_input("Enter your email address:")
#         if st.button("Subscribe", key="subscribe_button"):
#             if save_email(email):
#                 st.success("You've been subscribed for regular paper updates!")
#             else:
#                 st.error("There was an error subscribing. Please try again.")
    
#     with st.expander("📁 Upload Reference Material", expanded=True):
#         st.subheader("Enhance Our Knowledge Base")
#         uploaded_file = st.file_uploader("Choose a file to upload:")
#         if uploaded_file is not None:
#             if upload_material(uploaded_file):
#                 st.success("Material uploaded successfully!")
#             else:
#                 st.error("There was an error uploading the file. Please try again.")

# # Query History
# st.markdown("---")
# st.subheader("📜 Query History")
# if 'history' in st.session_state and st.session_state.history:
#     history_df = pd.DataFrame(st.session_state.history, columns=["Timestamp", "Query"])
#     history_df = history_df.sort_values("Timestamp", ascending=False).reset_index(drop=True)
#     st.dataframe(history_df, use_container_width=True)
# else:
#     st.info("No search history available yet. Start searching to see your history!")

# # Footer
# st.markdown("---")
# st.markdown("© 2024 Duke University AI Scholar Paper Retrieval | Built with ❤️ using Streamlit")