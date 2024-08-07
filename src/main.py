import asyncio
import semantic_kernel as sk
from agents_sk import ResearchTools

import os
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
import json
from utils import extract_parameters





async def chat(kernel, chat_history) -> bool:
    try:
        user_input = input("User:> ")
    except KeyboardInterrupt:
        print("\n\nExiting chat...")
        return False
    except EOFError:
        print("\n\nExiting chat...")
        return False

    if user_input == "exit":
        print("\n\nExiting chat...")
        return False


    
    #Extract keywords
    keywords = await kernel.invoke(
        function_name="get_keywords",
        plugin_name="research_tools", 
        kernel = kernel, chat_history = chat_history, query=user_input)
    
    results = str(keywords.value[0])
    params = extract_parameters(results)
    print(f"Mosscap:> {params}")
    
    
    #Save reuslts to dataframe
    keywords = await kernel.invoke(
        function_name="retrieve_papers",
        plugin_name="research_tools", 
        num_papers = 1,
        **params)
    
    
    
    chat_history.add_user_message(user_input)
    chat_history.add_assistant_message(str(keywords))
    return True, chat_history


async def main() -> None:
    
    # Initialize the kernel
    kernel = sk.Kernel()

    # Create ResearchTools instance
    research_tools = ResearchTools()
    kernel.add_plugin(research_tools, plugin_name="research_tools")
    research_tools.setup_llm(kernel)
    research_tools.setup_info_extractor()
    chat_history = ChatHistory()
    
    chatting = True
    while chatting:
        chatting, chat_history  = await chat(kernel, chat_history)


if __name__ == "__main__":
    asyncio.run(main())
    
# research_tools_chat_func = 