from langchain_core.tools import tool

from LLMs.LangChain.text_splitters.RecursiveCharacterTextSplitter import LangChain_RecursiveTextSplitter
from LLMs.LangChain.document_loaders.WikipediaLoader import LangChain_WikipediaLoader
from LLMs.LangChain.vector_stores.Chroma.index import LangChain_Chroma

@tool
def TOOL_LangChain_WikipediaLoader(ingredient):
    """
        Tool to add to the over all LLMs context w/ wikipedia data.
        I do NOT want this to simply answer the question as this tool will be in a line of tools available to append valuable inforamtion to the context PRIOR to answering the question.
    """
    # CONVERT: Wikipedia page into individual "documents"
    CLASS_INSTANCE_LangChain_WikipediaLoader = LangChain_WikipediaLoader(
        query=ingredient.name
    )
    documents = CLASS_INSTANCE_LangChain_WikipediaLoader.call_loader()
    # print(f'THE DOCUMENTS\n{documents}')

    # CONVERT: document to chunks w/ text splitter
    CLASS_INSTANCE_LangChain_RecursiveTextSplitter = LangChain_RecursiveTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len, 
    )
    chunks = CLASS_INSTANCE_LangChain_RecursiveTextSplitter.split_documents(documents)
    # print(f'THE CHUNKS\n{chunks}\n')

    # CONFIGURE: vector store
    CLASS_INSTANCE_LangChain_Chroma = LangChain_Chroma(
        type='from_documents',
        documents=chunks
    ) 
    # print(f'THE VECTOR STORE\n{CLASS_INSTANCE_LangChain_Chroma.vectorstore}\n')

    # CONFIGURE: retriever
    retriever = CLASS_INSTANCE_LangChain_Chroma.vectorstore.as_retriever()
    # print(f'THE RETRIEVER\n{retriever}\n')

    return [
        CLASS_INSTANCE_LangChain_Chroma, 
        documents, chunks, retriever
    ]

