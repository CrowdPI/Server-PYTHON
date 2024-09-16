from langchain_core.tools import tool

from langchain.prompts import PromptTemplate

from LLMs.LangChain.text_splitters.RecursiveCharacterTextSplitter import LangChain_RecursiveTextSplitter
from LLMs.LangChain.document_loaders.WikipediaLoader import LangChain_WikipediaLoader
from LLMs.LangChain.vector_stores.Chroma.index import LangChain_Chroma

@tool
def TOOL_LangChain_WikipediaLoader(ingredient, version=1):
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

    if version == 1:
        return [
            CLASS_INSTANCE_LangChain_Chroma, 
            documents, chunks, retriever
        ]

    if version == 2:
        """
        going against doc strings and calling the "complete" cycle instead of just updating the universal context
        """

        # CONFIGURE: prompt
        prompt_template = PromptTemplate.from_template(f"""
            You are a nutritionist AI that is tasked with providing a facts based summary of a provided Wikipedia webpage. 
            Focus your response on the nutritional aspects of the Wikipedia webpage.

            Do not mention who or what you are in your summarization. 

            Context: {context}
        """)

        # CONFIGURE: rag chain
        rag_chain = (
            {
                "context": retriever | format_docs, 
                "question": RunnablePassthrough()
            }
            | prompt_template
            | structured_llm
        )
        # print(f'THE RAG CHAIN\n{rag_chain}\n')

        # INVOKE: rag chain
        result = rag_chain.invoke(f"""
            Please summarize the following cooking ingredient:
        """)
        return result

