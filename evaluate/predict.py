import asyncio
import semantic_kernel as sk
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, AzureChatCompletion
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.connectors.ai.ollama.services.ollama_chat_completion import OllamaChatCompletion
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion
from semantic_kernel.connectors.ai.ollama.services.ollama_chat_completion import OllamaChatCompletion
from prompt import PromptStore
from utils import extract_parameters



"""

Set LLMs with Prompts

"""

# set LLMs
models = {}
promptstore = PromptStore()
keywords_extraction_prompt = promptstore.get_prompt("keywords_extraction_prompt")
for model in ["llama3", "mistral", "gemma"]:
    kernel = Kernel()
    kernel.add_service(OllamaChatCompletion(ai_model_id=model))
    kernel.add_function(
        plugin_name="KeywordsChatBot",
        function_name="KeywordsExtraction",
        prompt=keywords_extraction_prompt,
        template_format="semantic-kernel")
    models[model] = kernel

# set chatgpt as Baseline
kernel = Kernel()
api_key = ""
service_id = "local-gpt"
openAIClient = AsyncOpenAI(api_key=api_key)
kernel.add_service(OpenAIChatCompletion(service_id=service_id, ai_model_id="gpt-3.5-turbo", async_client=openAIClient))
settings = kernel.get_prompt_execution_settings_from_service_id(service_id)
settings.max_tokens = 2000
settings.temperature = 0.7
settings.top_p = 0.8
kernel.add_function(
    plugin_name="KeywordsChatBot",
    function_name="KeywordsExtraction",
    prompt=keywords_extraction_prompt,
    template_format="semantic-kernel",
    prompt_template_settings=settings)

models["baseline"] = kernel
async def get_keywords(query, model_name):
    kernel = models[model_name]
    result = await kernel.invoke(
        plugin_name="KeywordsChatBot",
        function_name="KeywordsExtraction",
        query=query
    )
    return result

"""

Get Predictions

"""


# evaluate key words extraction
loop = asyncio.get_event_loop() 
results = {}
file_path = './evaluate/keywords_extraction_query.txt'
for model_name in [ "gemma",]: # "baseline", ,, "mistral", "gemma", "llama3"
    results[model_name] = []
    with open(file_path, 'r') as file:
        for idx, line in enumerate(file):
            query = line.strip()
            result = loop.run_until_complete(get_keywords(query, model_name))
            params = extract_parameters(str(result.value[0]))
            results[model_name].append(params)
            print(params)
            # params = extract_parameters(str(asyncio.run(get_keywords(query, model_name)).value[0]))
            # results[model_name].append(params)
    import json
    # Define the path where you want to save the file
    file_path = f'./evaluate/outputs_{model_name}.json'
    # Open the file in write mode and save the dictionary as JSON
    with open(file_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)

import json
# Define the path where you want to save the file
file_path = './evaluate/final_outputs.json'
# Open the file in write mode and save the dictionary as JSON
with open(file_path, 'w') as json_file:
    json.dump(results, json_file, indent=4)
    
    
    