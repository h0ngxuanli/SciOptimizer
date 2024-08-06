
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.tools import FunctionTool
from llama_index.llms import Llama3
from llama_index.agent import ReActAgent

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

# basic tools
def retrieve_papers(query: str, max_results: int = 50) -> list:
    """
    Retrieve relevant papers based on user query from specified sources.
    """

    results = []
    search_query = scholarly.search_pubs(query)
    results.extend([next(search_query) for _ in range(max_results)])

    return results

def save_to_csv(papers: list, filename: str):
    """
    Save paper metadata to CSV file.
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['title', 'authors', 'year', 'url'])
        writer.writeheader()
        for paper in papers:
            writer.writerow({
                'title': paper.title,
                'authors': ', '.join(paper.authors),
                'year': paper.year,
                'url': paper.url
            })

def save_to_zotero(papers: list, library_id: str, api_key: str):
    """
    Save paper metadata to Zotero.
    """
    zot = zotero.Zotero(library_id, 'user', api_key)
    for paper in papers:
        template = zot.item_template('journalArticle')
        template['title'] = paper.title
        template['creators'] = [{'creatorType': 'author', 'name': author} for author in paper.authors]
        template['date'] = paper.year
        template['url'] = paper.url
        zot.create_items([template])



def fine_grained_retrieval(papers: list, filters: dict) -> list:
    """
    Further narrow down search results based on specific criteria.
    """
    filtered_papers = papers
    
    if 'authors' in filters:
        filtered_papers = [p for p in filtered_papers if any(author in p.authors for author in filters['authors'])]
    
    if 'year' in filters:
        filtered_papers = [p for p in filtered_papers if filters['year'][0] <= p.year <= filters['year'][1]]
    
    if 'publisher' in filters:
        filtered_papers = [p for p in filtered_papers if filters['publisher'] in p.publisher]
    
    if 'affiliation' in filters:
        filtered_papers = [p for p in filtered_papers if filters['affiliation'] in p.affiliations]
    
    if 'keywords' in filters:
        filtered_papers = [p for p in filtered_papers if any(keyword in p.keywords for keyword in filters['keywords'])]
    
    return filtered_papers




def generate_reference(paper, style: str) -> str:
    """
    Automatically generate references in the desired format.
    """
    # This is a simplified example. You'd need to implement the full logic for different citation styles.
    if style == 'apa':
        return f"{', '.join(paper.authors)} ({paper.year}). {paper.title}. {paper.journal}, {paper.volume}({paper.number}), {paper.pages}."
    elif style == 'mla':
        return f"{paper.authors[0]}, et al. \"{paper.title}.\" {paper.journal}, vol. {paper.volume}, no. {paper.number}, {paper.year}, pp. {paper.pages}."
    # Add more styles as needed



def get_citing_papers(paper_id: str, max_results: int = 50) -> list:
    """
    Retrieve metadata of papers that cite a specific paper.
    """
    s2_api = semanticscholar.SemanticScholar()
    citing_papers = s2_api.get_citing_papers(paper_id, limit=max_results)
    return citing_papers




def generate_survey_table(llm, papers: list, columns: dict) -> dict:
    """
    Build a customized survey table to summarize papers.
    """
    table = {}
    for col_name, col_value in columns.items():
        for paper in papers:
            table[col_name].append(llm.generate(f"{col_value}: {paper.abstract}"))

    return table


def schedule_updates(query: str, sources: list, frequency: str, email: str):
    """
    Schedule automatic updates for paper retrieval.
    """
    def job():
        new_papers = retrieve_papers(query, sources)
        if new_papers:
            send_email_notification(email, new_papers)
    if frequency == 'daily':
        schedule.every().day.at("09:00").do(job)
    elif frequency == 'weekly':
        schedule.every().monday.at("09:00").do(job)
    # Add more frequency options as needed

def send_email_notification(email: str, papers: list):
    """
    Send email notification about newly retrieved papers.
    """
    msg = MIMEMultipart()
    msg['From'] = 'hongxuan.li@duke.edu'
    msg['To'] = email
    msg['Subject'] = 'New Papers Retrieved'
    
    body = "The following new papers have been retrieved:\n\n"
    for paper in papers:
        body += f"Title: {paper.title}\nAuthors: {', '.join(paper.authors)}\nYear: {paper.year}\nURL: {paper.url}\n\n"
    
    msg.attach(MIMEText(body, 'plain'))
    


def get_tools():
    fine_grained_retrieval_tool = FunctionTool.from_defaults(
    fn=fine_grained_retrieval,
    name="FineGrainedRetrieval",
    description="Further narrows down search results based on specific criteria."
)

    generate_reference_tool = FunctionTool.from_defaults(
        fn=generate_reference,
        name="GenerateReference",
        description="Generates references in the specified format."
    )

    get_citing_papers_tool = FunctionTool.from_defaults(
        fn=get_citing_papers,
        name="GetCitingPapers",
        description="Retrieves metadata of papers that cite a specific paper."
    )


    generate_survey_table_tool = FunctionTool.from_defaults(
        fn=generate_survey_table,
        name="GenerateSurveyTable",
        description="Builds a customized survey table to summarize papers."
    )


    schedule_updates_tool = FunctionTool.from_defaults(
        fn=schedule_updates,
        name="ScheduleUpdates",
        description="Schedules automatic updates for paper retrieval."
    )


    retrieve_papers_tool = FunctionTool.from_defaults(
        fn=retrieve_papers,
        name="RetrievePapers",
        description="Retrieves relevant papers based on user query from specified sources."
    )

    save_to_csv_tool = FunctionTool.from_defaults(
        fn=save_to_csv,
        name="SaveToCSV",
        description="Saves paper metadata to a CSV file."
    )

    save_to_zotero_tool = FunctionTool.from_defaults(
        fn=save_to_zotero,
        name="SaveToZotero",
        description="Saves paper metadata to Zotero."
    )

    return [retrieve_papers_tool, save_to_csv_tool, save_to_zotero_tool,
            fine_grained_retrieval_tool, generate_reference_tool,
            get_citing_papers_tool, generate_survey_table_tool,
            schedule_updates_tool]
