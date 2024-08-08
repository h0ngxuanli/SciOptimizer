
import os
import logging
from pyzotero import zotero
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion
from semantic_kernel.functions import kernel_function
from scholarly import scholarly
from dotenv import load_dotenv
import pandas as pd
import datetime
import arxiv
from pathlib import Path
from semantic_kernel.connectors.ai.ollama.services.ollama_chat_completion import OllamaChatCompletion

from pyzotero import zotero
import sys
current_path = Path(__file__).resolve()
parent_path = current_path.parent.parent
sys.path.append(str(parent_path))
from src.prompt import PromptStore
from src.utils import extract_text_from_pdf


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


model_dict = dict(zip([
        "LLaMA-3",
        "LLaMA-2",
        "Mistral",
        "Gemma",
        "GPT-4",
        "GPT-3.5 Turbo",
    ], [
        "llama3",
        "llama2",
        "mistral",
        "gemma",
        "gpt-4",
        "gpt-3.5-turbo",
    ]))

class ResearchTools:
    
    
    def __init__(self, kernel, num_keywords = 5, model = None):
        self.num_keywords = num_keywords
        self.model = model
        self.kernel = kernel

    # @staticmethod
    def setup_llm(self):
        # ChatGPT service using official API
        load_dotenv()
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Please set the OPENAI_API_KEY environment variable")

        settings = None
        if self.model in ["GPT-4", "GPT-3.5 Turbo"]:
            service_id = "local-gpt"
            openAIClient: AsyncOpenAI = AsyncOpenAI(api_key=api_key)
            self.kernel.add_service(OpenAIChatCompletion(service_id=service_id, ai_model_id="gpt-3.5-turbo", async_client=openAIClient))
            settings = self.kernel.get_prompt_execution_settings_from_service_id(service_id)
            settings.max_tokens = 2000
            settings.temperature = 0.7
            settings.top_p = 0.8
        elif self.model in ["LLaMA-3", "LLaMA-2", "Mistral", "Gemma"]: 
            self.kernel.add_service(OllamaChatCompletion(ai_model_id=model_dict[self.model]))

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
        
        
        # add custom tasks
        for column in tabel_columns:
            promptstore.add_prompt(column)
            info_extraction_prompt = promptstore.get_prompt(column)
            self.kernel.add_function(
                plugin_name=column.replace(" ", "") + "ChatBot",
                function_name=column.replace(" ", ""),
                prompt= info_extraction_prompt,
                template_format="semantic-kernel",
                prompt_template_settings=self.settings,
            )
            
    async def get_survery_table(self, paper_text):
        table_info = {}
        for column in self.table_columns:        
            column_info = await self.kernel.invoke(
                                plugin_name = column.replace(" ", "")+"ChatBot",
                                function_name = column.replace(" ", ""),
                                paper_text = paper_text)
            table_info[column] = str(column_info.value[0])
        return table_info

    @kernel_function(
        description="Extract keywords from user query using LLM",
        name="get_keywords"
    )
    def get_keywords(self, query: str) -> str:
        keywords = self.kernel.invoke(
            plugin_name="KeywordsChatBot",
            function_name="KeywordsExtraction",
            query=query)
        return keywords


    @kernel_function(
        description="Retrieve relevant papers based on keywords",
        name="retrieve_papers"
    )
    async def retrieve_papers(self, num_papers, keywords=None, year_range=None, authors=None, institutions=None, conferences=None) -> list:
        
        
        time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
        paper_path = f"./results/papers/{time}"
        # info_path = f"../results/info/{time}"
        os.makedirs(paper_path, exist_ok=True)

        year_range = [int(year) for year in year_range]
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
                    'keywords': f"{', '.join(keywords)}" if keywords else 'N/A'
                }
                
            
            paper.download_pdf(dirpath=paper_path, filename=f"{paper.title.replace(' ', '_')}.pdf")
            file_path = paper_path + "/" + f"{paper.title.replace(' ', '_')}.pdf"
            
            if os.path.exists(file_path):
                paper_text = extract_text_from_pdf(file_path)
            
                table_info = await self.get_survery_table(paper_text = paper_text)
                
                result.update(table_info)
            results.append(result)
        df = pd.DataFrame(results)    
        df.to_csv(f"./results/info/{time}.csv", index=False, encoding='utf-8-sig')
        return results


    @kernel_function(
        description="Save paper metadata to Zotero.",
        name="save_to_zotero"
    )
    def save_to_zotero(self, papers, USER_ID, LIBRARY_TYPE, API_KEY) -> bool:

        # # Replace these with your own values
        # API_KEY = 'C9HQpU9iLG6ZAqJMEzVE8BLq'
        # USER_ID = '8443872'
        # LIBRARY_TYPE = 'user'  # or 'group' if you're accessing a group library
        
        zot = zotero.Zotero(USER_ID, LIBRARY_TYPE, API_KEY)

        
        for paper in papers:
            paper_item = {}            
            paper_item['itemType'] = 'journalArticle'
            paper_item['title'] = paper['title']
            # paper_item['creators'] = [paper['author']]
            paper_item['date'] = paper['year']
            paper_item['url'] = paper['url']
            response = zot.create_items([paper_item])
            if 'successful' in response and response['successful']:
                print("Paper added successfully!")
                
                return True
            else:
                print("Failed to add paper:", response)
                
                return False