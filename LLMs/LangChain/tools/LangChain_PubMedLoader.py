from langchain_core.tools import tool

from LLMs.LangChain.text_splitters.RecursiveCharacterTextSplitter import LangChain_RecursiveTextSplitter
from LLMs.LangChain.document_loaders.PubMedLoader import LangChain_PubMedLoader
from LLMs.LangChain.vector_stores.Chroma.index import LangChain_Chroma

@tool
def TOOL_LangChain_PubMedLoader(ingredient):
    """
        Tool to add to the over all LLMs context w/ PubMed data.
        I do NOT want this to simply answer the question as this tool will be in a line of tools available to append valuable inforamtion to the context PRIOR to answering the question.
    """
    # CONVERT: PubMed data into "documents"
    CLASS_INSTANCE_LangChain_PubMed = LangChain_PubMedLoader(
        query=ingredient.name
    )
    documents = CLASS_INSTANCE_LangChain_PubMed.load()

    # Filter complex metadata
    for doc in documents:
        if isinstance(doc.metadata, Document):
            doc.metadata = filter_complex_metadata(doc.metadata)
        else:
            # If metadata is a string or not a dict, handle it accordingly
            doc.metadata = {"note": "No structured metadata available"}
            
        doc_dict = {
            "page_content": doc.page_content,
            "metadata": doc.metadata
        }
        # print('THE CURRENT DOCUMENT:')
        # print(json.dumps(doc_dict, indent=4, default=str))

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