
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
import requests
from scholarly import ProxyGenerator



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
        
    def setup_info_extractor(self):
        promptstore = PromptStore()
        
        
        keywords_extraction_prompt = promptstore.get_prompt("keywords_extraction_prompt")
        self.kernel.add_function(
            plugin_name="KeywordsChatBot",
            function_name="KeywordsExtraction",
            prompt= keywords_extraction_prompt,
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
        description="Extract what model is used",
        name="get_model"
    )
    def get_model(self, kernel, chat_history, query: str) -> str:
        keywords = kernel.invoke(
            plugin_name="KeywordsChatBot",
            function_name="KeywordsExtraction",
            chat_history = chat_history, query=query)
        return keywords
    
    
    @kernel_function(
        description="Extract keywords from user query using LLM",
        name="get_keywords"
    )
    def get_summary(self, kernel, chat_history, query: str) -> str:
        keywords = kernel.invoke(
            plugin_name="KeywordsChatBot",
            function_name="KeywordsExtraction",
            chat_history = chat_history, query=query)
        return keywords

    @kernel_function(
        description="Extract keywords from user query using LLM",
        name="get_keywords"
    )
    def get_summary(self, kernel, chat_history, query: str) -> str:
        keywords = kernel.invoke(
            plugin_name="KeywordsChatBot",
            function_name="KeywordsExtraction",
            chat_history = chat_history, query=query)
        return keywords




    # # Download papers

    # @kernel_function(
    #     description="Retrieve relevant papers based on keywords",
    #     name="retrieve_papers"
    # )
    # def retrieve_papers(self, num_papers, keywords=None, year_range=None, authors=None, institutions=None, conferences=None) -> list:
    #     # Construct the search query based on provided parameters
        
    #     time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    #     paper_path = f"../results/papers/{time}"
    #     info_path = f"../results/info/{time}"
    #     os.makedirs(paper_path, exist_ok=True)
    #     os.makedirs(info_path, exist_ok=True)
        
    #     query_parts = []
    #     if keywords:
    #         query_parts.append(f"{' '.join(keywords)}")
    #     if year_range:
    #         year_query = ' OR '.join([f'{year}' for year in year_range])
    #         query_parts.append(f'({year_query})')
    #     if authors:
    #         author_query = ' OR '.join([f'author:{author}' for author in authors])
    #         query_parts.append(f'({author_query})')
    #     if institutions:
    #         institution_query = ' OR '.join([f'institution:{institution}' for institution in institutions])
    #         query_parts.append(f'({institution_query})')
    #     if conferences:
    #         conference_query = ' OR '.join([f'conference:{conference}' for conference in conferences])
    #         query_parts.append(f'({conference_query})')
        
    #     query = ' '.join(query_parts)
        
    #     # Set up SerpApi parameters
    #     params = {
    #         "engine": "google_scholar",
    #         "q": query,
    #         "api_key": os.environ.get("SERP_API_KEY"),
    #         "num": num_papers
    #     }
        
    #     search = GoogleSearch(params)
    #     results = search.get_dict()
        
    #     papers = []
    #     for num, pub in enumerate(results.get('organic_results', [])):
    #         result = {
    #             'title': pub.get('title', 'N/A'),
    #             'year': pub.get('publication_info', {}).get('year', 'N/A'),
    #             'author': ', '.join([author.get('name', '') for author in pub.get('publication_info', {}).get('authors', [])]),
    #             'institution': pub.get('publication_info', {}).get('publisher', 'N/A'),
    #             'conference': pub.get('publication_info', {}).get('venue', 'N/A'),
    #             'url': pub.get('link', 'N/A'),
    #             'abstract': pub.get('snippet', 'N/A'),
    #             'keywords': f"keywords: {', '.join(keywords)}" if keywords else 'N/A'
    #         }
    #         papers.append(result)
            
    #         url = pub.get('link', 'N/A')
    #         if url != 'N/A':
    #             response = requests.get(url)
    #             if response.status_code == 200:
    #                 filename = pub.get('title', 'N/A')['title'].replace(' ', '_') + '.pdf'
    #                 with open(f"{paper_path}/{filename}", 'wb') as f:
    #                     f.write(response.content)
    #         if num == num_papers - 1:
    #             break
        
        
    #     df = pd.DataFrame(papers)    
    #     df.to_csv(f"../results/info/{time}.csv", index=False, encoding='utf-8-sig')
    #     return papers

    @kernel_function(
        description="Retrieve relevant papers based on keywords",
        name="retrieve_papers"
    )
    def retrieve_papers(self, num_papers, keywords=None, year_range=None, authors=None, institutions=None, conferences=None) -> list:
        # Construct the search query based on provided parameters
        
        
        
        # Set up a ProxyGenerator object to use free proxies
        # This needs to be done only once per session
        pg = ProxyGenerator()
        pg.FreeProxies()
        scholarly.use_proxy(pg)

        # # Now search Google Scholar from behind a proxy
        # search_query = scholarly.search_pubs('Perception of physical stability and center of mass of 3D objects')
        # scholarly.pprint(next(search_query))
        
        
        query_parts = []
        if keywords:
            query_parts.append(f"keywords: {', '.join(keywords)}")
        if year_range:
            year_query = ' OR '.join([f'year:{year}' for year in year_range])
            query_parts.append(f'({year_query})')
        if authors:
            author_query = ' OR '.join([f'author:{author}' for author in authors])
            query_parts.append(f'({author_query})')
        if institutions:
            institution_query = ' OR '.join([f'institution:{institution}' for institution in institutions])
            query_parts.append(f'({institution_query})')
        if conferences:
            conference_query = ' OR '.join([f'conference:{conference}' for conference in conferences])
            query_parts.append(f'({conference_query})')
        
        query = ' '.join(query_parts)
        
        # Perform the search
        search_query = scholarly.search_pubs(query)
        
        results = []
        for num, pub in enumerate(search_query):
            pub = scholarly.fill(pub)
            result = {
                'title': pub['bib'].get('title', 'N/A'),
                'year': pub['bib'].get('pub_year', 'N/A'),
                'author': pub['bib'].get('author', ""),
                'institution': pub['bib'].get('institution', 'N/A'),
                'conference': pub['bib'].get('venue', 'N/A'),
                'url': pub.get('pub_url', 'N/A'),
                'abstract': pub['bib'].get('abstract', 'N/A'),
                'keywords': f"keywords: {', '.join(keywords)}"
            }
            results.append(result)
            if num == num_papers:
                break
        print(111111111)
        print(results)
        time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
        df = pd.DataFrame(results)    
        df.to_csv(f"../results/info/{time}.csv", index = False, encoding='utf-8-sig')
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
