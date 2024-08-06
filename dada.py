import semantic_kernel as sk
from semantic_kernel.skill_definition import sk_function, sk_function_context_parameter
from semantic_kernel.orchestration.sk_context import SKContext
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings import LLaMAEmbeddings
from llama_index.llms import LLaMA
import pybtex
import arxiv
import scholarly
import semanticscholar
import csv
from pyzotero import zotero
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize the kernel
kernel = sk.Kernel()

# LLaMA 3 service
llm = LLaMA(model_path="./model")
kernel.add_text_completion_service("llama3", llm)

# Load documents and create a vector store
documents = SimpleDirectoryReader('./materials').load_data()
index = VectorStoreIndex.from_documents(documents, embedding_model=LLaMAEmbeddings())

class ResearchTools:

    @sk_function(
        description="Retrieve relevant papers based on user query from specified sources.",
        name="retrieve_papers"
    )
    @sk_function_context_parameter(name="query", description="The search query")
    @sk_function_context_parameter(name="max_results", description="Maximum number of results to retrieve")
    def retrieve_papers(self, context: SKContext) -> str:
        query = context["query"]
        max_results = int(context["max_results"])
        results = []
        search_query = scholarly.search_pubs(query)
        results.extend([next(search_query) for _ in range(max_results)])
        return str(results)

    @sk_function(
        description="Extract keywords from user query with context.",
        name="extract_keywords"
    )
    @sk_function_context_parameter(name="user_description", description="The user description")
    def extract_keywords(self, context: SKContext) -> str:
        user_description = context["user_description"]
        # Retrieve relevant documents
        query_engine = index.as_query_engine()
        response = query_engine.query(user_description)
        context_text = response.response
        # Create a prompt for keyword extraction
        prompt = f"""
        Given the following context and user query, extract the most relevant keywords for a Google Scholar search.

        Context: {context_text}
        User Query: {user_description}

        Keywords:
        """
        # Use LLaMA to extract keywords
        keywords = kernel.create_semantic_function(prompt)(user_description)
        return keywords.strip()


# Add the ResearchTools plugin to the kernel
kernel.import_skill(ResearchTools(), skill_name="research_tools")

# Main function to process user query
def process_user_query(user_description):
    context = SKContext(variables={"user_description": user_description})
    keywords = kernel.run_async(kernel.skills.research_tools.extract_keywords, input_vars=context.variables)
    return keywords

# Example usage
user_description = "I need papers on quantum computing applications in cryptography"
keywords = process_user_query(user_description)
print(f"Extracted Keywords: {keywords}")