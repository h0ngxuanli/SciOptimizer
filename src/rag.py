import openai
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter


openai.api_key = ''
llm = OpenAI(temperature=0, openai_api_key=openai.api_key)

# Load documents and create a vector store
documents = ["Quantum computing is a rapidly evolving field with significant implications for cryptography.",
             "Cryptography is essential for secure communication in the digital age.",
             "Machine learning techniques are being applied to quantum computing for optimization."]
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = [TextLoader(doc).load_and_split(text_splitter) for doc in documents]
flat_docs = [item for sublist in docs for item in sublist]

# Create embeddings and vector store
embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
vectorstore = FAISS.from_documents(flat_docs, embeddings)

# Create a retriever from the vector store
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Define the prompt template for keyword extraction
keyword_extraction_prompt = PromptTemplate(
    input_variables=["context", "query"],
    template="""
    Given the following context and user query, extract the most relevant keywords for a Google Scholar search.

    Context: {context}
    User Query: {query}

    Keywords:
    """
)

# Create the RetrievalQA chain
retrieval_qa_chain = RetrievalQA(
    retriever=retriever,
    llm=llm,
    prompt_template=keyword_extraction_prompt,
    return_source_documents=False
)

# Main function to process user query
def process_user_query(user_description):
    # Retrieve relevant documents to add context
    retrieved_docs = retriever.get_relevant_documents(user_description)
    context = " ".join([doc.page_content for doc in retrieved_docs])

    # Form the prompt with context and user query
    prompt = keyword_extraction_prompt.format(context=context, query=user_description)

    # Extract keywords using the LLM
    response = llm(prompt)
    keywords = response.strip()
    
    return keywords

# Example usage
user_description = "I need papers on quantum computing applications in cryptography"
keywords = process_user_query(user_description)
print(f"Extracted Keywords: {keywords}")