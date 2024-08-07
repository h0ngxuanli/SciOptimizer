
import os
import csv
import logging
from pyzotero import zotero
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion
from semantic_kernel.functions import kernel_function
import json
from scholarly import scholarly
from dotenv import load_dotenv
import pandas as pd
import datetime
from prompt import PromptStore
from serpapi import GoogleSearch
import arxiv
import requests



# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class ResearchTools:
    
    
    def __init__(self, num_keywords = 5, model = None):
        self.num_keywords = num_keywords
        self.model = model

    # @staticmethod
    def setup_llm(self, kernel):
        # ChatGPT service using official API
        load_dotenv()
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Please set the OPENAI_API_KEY environment variable")

        service_id = "local-gpt"
        openAIClient: AsyncOpenAI = AsyncOpenAI(api_key=api_key)
        kernel.add_service(OpenAIChatCompletion(service_id=service_id, ai_model_id="gpt-3.5-turbo", async_client=openAIClient))
        settings = kernel.get_prompt_execution_settings_from_service_id(service_id)
        settings.max_tokens = 2000
        settings.temperature = 0.7
        settings.top_p = 0.8
        self.kernel = kernel
        self.settings = settings
        
    def setup_info_extractor(self, tabel_columns):
        self.table_columns = tabel_columns
        
        promptstore = PromptStore()
        
        keywords_extraction_prompt = promptstore.get_prompt("keywords_extraction_prompt")
        self.kernel.add_function(
            plugin_name="KeywordsChatBot",
            function_name="KeywordsExtraction",
            prompt= keywords_extraction_prompt,
            template_format="semantic-kernel",
            prompt_template_settings=self.settings,
        )
        
        for column in range(tabel_columns):
            info_extraction_prompt = promptstore.get_prompt("keywords_extraction_prompt")
            
            
            
            self.kernel.add_function(
                plugin_name=column + "ChatBot",
                function_name=column,
                prompt= info_extraction_prompt,
                template_format="semantic-kernel",
                prompt_template_settings=self.settings,
            )

    @kernel_function(
        description="Extract keywords from user query using LLM",
        name="get_keywords"
    )
    def get_keywords(self, kernel, chat_history, query: str) -> str:
        keywords = kernel.invoke(
            plugin_name="KeywordsChatBot",
            function_name="KeywordsExtraction",
            chat_history = chat_history, query=query)
        return keywords


    @kernel_function(
        description="Retrieve relevant papers based on keywords",
        name="retrieve_papers"
    )
    def retrieve_papers(self, num_papers, keywords=None, year_range=None, authors=None, institutions=None, conferences=None) -> list:
       
       
        time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
        paper_path = f"../results/papers/{time}"
        info_path = f"../results/info/{time}"
        os.makedirs(paper_path, exist_ok=True)
        os.makedirs(info_path, exist_ok=True)
       
       
        # Construct the search query based on provided parameters
        query_parts = []
        if keywords:
            query_parts.extend(keywords)
        if authors:
            query_parts.extend([f"au:{author}" for author in authors])
        if institutions:
            query_parts.extend([f"inst:{institution}" for institution in institutions])
        if conferences:
            query_parts.extend([f"co:{conference}" for conference in conferences])
        
        query = ' AND '.join(query_parts)
        
        # Set up the search parameters
        search = arxiv.Search(
            query=query,
            max_results=num_papers,
            sort_by=arxiv.SortCriterion.Relevance,
            sort_order=arxiv.SortOrder.Descending
        )
        
        # If year range is provided, we'll filter results later
        min_year = int(min(year_range)) if year_range else None
        max_year = int(max(year_range)) if year_range else None
        
        # Perform the search
        client = arxiv.Client()
        results = []
        
        for paper in client.results(search):
            # Check if the paper's year is within the specified range
            paper_year = paper.published.year
            if (min_year is None or paper_year >= min_year) and (max_year is None or paper_year <= max_year):
                result = {
                    'title': paper.title,
                    'year': paper.published.year,
                    'author': ', '.join([author.name for author in paper.authors]),
                    # 'institution': 'N/A',  # arXiv API doesn't provide institution information
                    # 'conference': 'N/A',  # arXiv API doesn't provide conference information
                    'url': paper.pdf_url,
                    'abstract': paper.summary,
                    'keywords': f"keywords: {', '.join(keywords)}" if keywords else 'N/A'
                }
                
            
            paper.download_pdf(dirpath=paper_path, filename=f"{paper.title.replace(' ', '_')}.pdf")
            results.append(result)
        
        
        time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
        df = pd.DataFrame(results)    
        df.to_csv(f"../results/info/{time}.csv", index=False, encoding='utf-8-sig')
        return results


    # def download_paper(url, title):
    #     try:
    #         response = requests.get(url)
    #         response.raise_for_status()  # Check if the request was successful
    #         file_name = f"{title}.pdf".replace('/', '_')  # Replace slashes to avoid directory issues
    #         with open(file_name, 'wb') as file:
    #             file.write(response.content)
    #         print(f"Downloaded: {file_name}")
    #     except requests.exceptions.RequestException as e:
    #         print(f"Failed to download {title}: {e}")


    # @kernel_function(
    #     description="Save paper metadata to Zotero.",
    #     name="save_to_zotero"
    # )
    # def save_to_zotero(self, papers: str, library_id: str, api_key: str) -> str:
    #     papers = json.loads(papers)
    #     try:
    #         zot = zotero.Zotero(library_id, 'user', api_key)
    #         for paper in papers:
    #             template = zot.item_template('journalArticle')
    #             template['title'] = paper['title']
    #             template['creators'] = [{'creatorType': 'author', 'name': author} for author in paper['author']]
    #             template['date'] = paper['year']
    #             template['url'] = paper['url']
    #             zot.create_items([template])
    #     except Exception as e:
    #         logger.error(f"Error saving to Zotero: {e}")
    #         return str(e)
        
    #     return "Papers saved to Zotero"
