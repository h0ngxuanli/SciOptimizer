import pytest
import sys
from unittest.mock import Mock, patch, AsyncMock, create_autospec
from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion
from semantic_kernel.connectors.ai.ollama.services.ollama_chat_completion import OllamaChatCompletion
from pathlib import Path
from openai import AsyncOpenAI
import os
import pandas as pd

current_path = Path(__file__).resolve()
parent_path = current_path.parent.parent
sys.path.append(str(parent_path))

from src.agents_sk import ResearchTools
from src.prompt import PromptStore
from src.utils import extract_text_from_pdf

@pytest.fixture
def research_tools():
    kernel = Mock(spec=Kernel)
    return ResearchTools(kernel, num_keywords=5, model="GPT-3.5 Turbo")

# Test initialization of ResearchTools
def test_init(research_tools):
    assert research_tools.num_keywords == 5
    assert research_tools.model == "GPT-3.5 Turbo"
    assert isinstance(research_tools.kernel, Mock)




# Test setup of OpenAI LLM
def test_setup_llm_openai(research_tools):
    mock_async_openai = create_autospec(AsyncOpenAI)
    with patch('src.agents_sk.AsyncOpenAI', return_value=mock_async_openai):
        with patch.object(research_tools.kernel, 'add_service') as mock_add_service:
            with patch.object(research_tools.kernel, 'get_prompt_execution_settings_from_service_id', return_value=Mock()) as mock_get_settings:
                research_tools.setup_llm(api_key="test_api_key")
                
                mock_add_service.assert_called_once()
                mock_get_settings.assert_called_once_with("local-gpt")
                assert hasattr(research_tools, 'settings')

# Test setup of Ollama LLM
def test_setup_llm_ollama(research_tools):
    research_tools.model = "LLaMA-2"
    with patch.object(research_tools.kernel, 'add_service') as mock_add_service:
        research_tools.setup_llm()
        mock_add_service.assert_called_once()

# Test setup of information extractor
def test_setup_info_extractor(research_tools):
    research_tools.settings = Mock()
    with patch('src.prompt.PromptStore') as mock_prompt_store:
        mock_prompt_store_instance = mock_prompt_store.return_value
        mock_prompt_store_instance.get_prompt.return_value = "test_prompt"
        
        with patch.object(research_tools.kernel, 'add_function') as mock_add_function:
            research_tools.setup_info_extractor(["column1", "column2"])
            
            assert research_tools.table_columns == ["column1", "column2"]
            assert mock_add_function.call_count == 3  # 1 for keywords extraction + 2 for columns
            
            
            

# Test asynchronous get_survey_table method
@pytest.mark.asyncio
async def test_async_get_survey_table(research_tools):
    research_tools.table_columns = ["column1", "column2"]
    research_tools.kernel.invoke = AsyncMock(return_value=Mock(value=["test_value"]))
    
    result = await research_tools.get_survey_table("test_paper_text")
    
    assert result == {"column1": "test_value", "column2": "test_value"}
    assert research_tools.kernel.invoke.call_count == 2

# Test get_keywords method
def test_get_keywords(research_tools):
    research_tools.kernel.invoke = Mock(return_value="test_keywords")
    
    result = research_tools.get_keywords("test_query")
    
    assert result == "test_keywords"
    research_tools.kernel.invoke.assert_called_once_with(
        plugin_name="KeywordsChatBot",
        function_name="KeywordsExtraction",
        query="test_query"
    )




# Test asynchronous retrieve_papers method
@pytest.mark.asyncio
async def test_async_retrieve_papers(research_tools):
    with patch('src.agents_sk.arxiv') as mock_arxiv, \
         patch('src.agents_sk.extract_text_from_pdf') as mock_extract_text, \
         patch('pandas.DataFrame.to_csv') as mock_to_csv, \
         patch('os.makedirs') as mock_makedirs, \
         patch('os.path.exists', return_value=True):
        
        mock_search = Mock()
        mock_arxiv.Search.return_value = mock_search
        mock_client = Mock()
        mock_arxiv.Client.return_value = mock_client
        
        class Author:
            def __init__(self, name):
                self.name = name

        mock_paper = Mock(
            title="Test Paper",
            published=Mock(year=2023),
            authors=[Author("Author 1"), Author("Author 2")],
            pdf_url="http://test.com/paper.pdf",
            summary="Test summary",
            download_pdf=Mock()
        )
        mock_client.results.return_value = [mock_paper]
        mock_extract_text.return_value = "Extracted text"
        
        research_tools.get_survey_table = AsyncMock(return_value={"column1": "value1"})
        
        result = await research_tools.retrieve_papers(num_papers=1, keywords=["AI"])
        
        assert len(result) == 1
        assert result[0]['title'] == "Test Paper"
        assert result[0]['year'] == 2023
        assert result[0]['author'] == "Author 1, Author 2"
        assert result[0]['url'] == "http://test.com/paper.pdf"
        assert result[0]['abstract'] == "Test summary"
        assert result[0]['keywords'] == "AI"
        assert result[0]['column1'] == "value1"
        
        mock_paper.download_pdf.assert_called_once()
        mock_extract_text.assert_called_once()
        research_tools.get_survey_table.assert_called_once_with(paper_text="Extracted text")
        mock_to_csv.assert_called_once()
        mock_makedirs.assert_called_once()

# Test save_to_zotero method
def test_save_to_zotero(research_tools):
    with patch('src.agents_sk.zotero.Zotero') as mock_zotero:
        mock_zotero_instance = mock_zotero.return_value
        mock_zotero_instance.create_items.return_value = {'successful': True}
        
        result = research_tools.save_to_zotero(
            papers=[{'title': 'Test Paper', 'year': '2023', 'url': 'http://test.com'}],
            USER_ID='test_user',
            LIBRARY_TYPE='user',
            API_KEY='test_api_key'
        )
        assert result == True
        mock_zotero.assert_called_once_with('test_user', 'user', 'test_api_key')
        mock_zotero_instance.create_items.assert_called_once()