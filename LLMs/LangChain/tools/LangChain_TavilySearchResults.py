from langchain.tools import tool

from langchain_community.tools.tavily_search import TavilySearchResults

@tool
def TOOL_LangChain_WebSearch(query: str) -> str:
    """Performs a web search"""
    tool = TavilySearchResults()
    docs = tool.invoke({
        "query": query
    })
    web_results = "\n".join([
        d["content"] for d in docs
    ])

    return web_results