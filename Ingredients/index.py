# IMPORTS
import os
import json

# IMPORTS > api server
from flask import Blueprint, jsonify, request

# IMPORTS > database
from models import Ingredient
from models import Summary
from database import db
from sqlAlchemy import session 

# IMPORTS > LLMs
from langchain_chroma import Chroma
import bs4
import openai
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.runnables import RunnablePassthrough
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from typing import Optional
# IMPORT > LLMs
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from LLMs.LangChain.text_splitters.RecursiveCharacterTextSplitter import LangChain_RecursiveTextSplitter
from LLMs.LangChain.vector_stores.Chroma.index import LangChain_Chroma
from LLMs.LangChain.OpenAI.ChatOpenAI import LangChain_OpenAI_ChatOpenAI
from langchain_community.vectorstores.utils import filter_complex_metadata

# IMPORT > LLMs > Document Loaders
from LLMs.LangChain.document_loaders.PubMedLoader import LangChain_PubMedLoader
from LLMs.LangChain.document_loaders.WikipediaLoader import LangChain_WikipediaLoader
# IMPORT > LLMs > tools
from LLMs.LangChain.tools.LangChain_WikipediaLoader import TOOL_LangChain_WikipediaLoader
from LLMs.LangChain.tools.LangChain_PubMedLoader import TOOL_LangChain_PubMedLoader
# IMPORT > tools
from tools.RagChain import TOOL_RagChain

# IMPORT > subrouter
ingredients_blueprint = Blueprint('ingredients', __name__)

# IMPORT > models
from Ingredients.models.PostIngredientSummary import PostIngredientSummary

####################
# HELPER FUNCTIONS #
####################
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@ingredients_blueprint.route('/ingredients', methods=["GET"])
def get_ingredients():
    ingredients = session.query(Ingredient).order_by(Ingredient.name.asc()).all()
    return jsonify([{
        "id": ing.id,
        "name": ing.name,
        "alias": ing.alias
    } for ing in ingredients]), 200

@ingredients_blueprint.route('/ingredients/<id>', methods=['GET'])
def get_ingredient(id):
    ingredient = session.query(Ingredient).get(int(id))
    if ingredient is None:
        return jsonify({"error": "Ingredient not found"}), 204
    return jsonify({
        "id": ingredient.id,
        "name": ingredient.name,
        "alias": ingredient.alias
    }), 200

# ROUTES > LLMs
# ROUTES > LLMs : summarize ingredient

@ingredients_blueprint.route('/ingredients/<id>/summarize', methods=['PUT']) # TODO: add a query param for model and set default to "gpt-4o"
def summarize_ingredient_single_source(id):
    # EXTRACT: model from query
    model = request.args.get('model', 'gpt-4o')
    print(f'THE MODEL\n{model}')

    # FETCH: ingredient from database
    ingredient = session.query(Ingredient).get(int(id))
    if ingredient is None:
        return jsonify({"error": "Ingredient not found"}), 204

    # CREATE: structured llm instanceq
    CLASS_INSTANCE_ChatOpenAI = LangChain_OpenAI_ChatOpenAI(
        model=model,
        temperature=0,
        max_tokens=None,
        json_mode=True
        # logprobs=
        # stream_options=
    )

    # FETCH: llm instance
    llm = CLASS_INSTANCE_ChatOpenAI.get_llm()

    class ChatOpenAI_Summary(BaseModel):
        """
        Summarize a specified dietary ingredient.
        """
        summary: str = Field(description="The summary of the specified dietary ingredient.")
        warnings: str = Field(description="A highlight of any potential health risks associated with the specified dietary ingredient.")
    structured_llm = llm.with_structured_output(ChatOpenAI_Summary)

    # CONFIGURE: ingredient summarization prompt
    messages = [
        (
            "system",
            f"""
                You are a helpful nutritionist that is tasked with providing a facts based summary of a provided dietary ingredient. Do not mention who or what you are in your summarization.
            """
        ),
        (
            "human",
            f"""
                Please summarize the following ingredient: {ingredient.name}.

                Along with the summary please provide a highlighted section for any warnings or negative aspects of the ingredient in question.
            """
        ),
    ]

    # INVOKE: structures LLM for summarization of ingredient
    result = structured_llm.invoke(messages)
    print(f'THE RESULT {result}')
    print(f'\t1 - THE RESULT.summary\n\t\t{result.summary}')
    print(f'\t2 - THE RESULT.warnings\n\t\t{result.warnings}')

    # UPDATE > ingredient summary
    PostIngredientSummary(
        ingredient_id=int(id), 
        summary=result.summary, 
        warnings=result.warnings,
        model=model,
        sources=['ChatOpenAI']
    )

    # RETURN
    return jsonify('success'), 200

@ingredients_blueprint.route('/ingredients/<id>/summarize/ragchain/<source>', methods=['PUT'])
def summarize_ingredient_ragchain(id, source):
    """
    Summarize ingredient information from a specified source.

    This route fetches an ingredient from the database by its ID and is intended
    to summarize information about the ingredient from a given source (e.g., Wikipedia).

    Args:
        id (str): The ID of the ingredient to summarize.
        source (str): The source of information to summarize from (not used in current implementation).

    Returns:
        ...TBD...

    Links:
        - Main Class ipynb: https://github.com/BloomTechAI/1.3-langsmith-langfuse/blob/e12b955ea9818d0d288f688f14b332d7eedd66ae/langsmith_rag.ipynb#L12
    """
    # EXTRACT: model from query
    model = request.args.get('model', 'gpt-4o')

    # Fetch ingredient from database
    ingredient = session.query(Ingredient).get(int(id))
    if (ingredient is None or ingredient.wikipedia is None):
        return jsonify({"error": "Ingredient or Wikipedia page not found"}), 204

    # CREATE: structured llm instanceq
    CLASS_INSTANCE_ChatOpenAI = LangChain_OpenAI_ChatOpenAI(
        model=model,
        temperature=0,
        max_tokens=None,
        json_mode=True
        # logprobs=
        # stream_options=
    )

    # FETCH: llm instance
    llm = CLASS_INSTANCE_ChatOpenAI.get_llm()

    class ChatOpenAI_Summary(BaseModel):
        """
        Summarize a specified dietary ingredient.
        """
        summary: str = Field(description="The summary of the specified dietary ingredient.")
        warnings: str = Field(description="A highlight of any potential health risks associated with the specified dietary ingredient.")
    structured_llm = llm.with_structured_output(ChatOpenAI_Summary)

    if source == 'wikipedia':
        # CONVERT: Wikipedia page into individual "documents"
        CLASS_INSTANCE_LangChain_WikipediaLoader = LangChain_WikipediaLoader(
            query=ingredient.name
        )
        documents = CLASS_INSTANCE_LangChain_WikipediaLoader.call_loader()
        # print(f'THE DOCUMENTS\n{documents}')
    

    if source == 'pubmed':
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

    # CONFIGURE: prompt
    prompt_template = PromptTemplate.from_template("""
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
    print(f'🎉 THE RESULT\n{result}')
    print(f'\t1 - THE RESULT.summary\n\t\t{result.summary}')
    print(f'\t2 - THE RESULT.warnings\n\t\t{result.warnings}')

    # UPDATE > ingredient summary
    PostIngredientSummary(
        ingredient_id=int(id), 
        summary=result.summary, 
        warnings=result.warnings,
        model=model,
        sources=[source]
    )

    # RETURN
    return jsonify('success'), 200


@ingredients_blueprint.route('/ingredients/<id>/summarize/toolchain', methods=['PUT'])
def summarize_ingredient_toolchain(id, version=2):
    # EXTRACT: model from query
    model = request.args.get('model', 'gpt-4o')

    # Fetch ingredient from database
    ingredient = session.query(Ingredient).get(int(id))
    if (ingredient is None or ingredient.wikipedia is None):
        return jsonify({"error": "Ingredient or Wikipedia page not found"}), 204

    if version == 2:
        # CREATE: llm instance
        llm = ChatOpenAI(
            model=model,
            temperature=0,
            max_tokens=None,
            # logprobs=
            # stream_options=
        )

        # BIND: tools to llm instance
        llm_with_tools = llm.bind_tools([
            TOOL_LangChain_WikipediaLoader,

            # TOOL_LangChain_PubMedLoader, 
            # TOOL_RagChain,
        ])
        # Debugging: Print bound tools
        # print(f'DEBUG: Bound Tools: {llm.tools}')  # THERE ARE NO ATTACHED TOOLS!! Check if tools are bound

        # INVOKE: structured LLM w/ tools
        result = llm_with_tools.invoke(f"""
            Please summarize the following ingredient: {ingredient.name}. 
            First, use the WikipediaLoader tool to fetch information about the ingredient. 
            Then, based on that information, provide a summary and any potential health warnings.
        """)
        print(f'WHAT IS THE RESULT\n{result}')
        print(f'WHAT ARE THE TOOL CALLS\n{result.tool_calls}') ## TODO: there are none!

        # UPDATE > ingredient summary
        summary_data = {
            'ingredient_id': int(id),
            'summary': result.content, 
            'model': model,
            'sources': ['toolchain:', 'wikipedia']
        }
        if hasattr(result, 'warnings'):
            if result.warnings:
                summary_data['warnings'] = result.warnings

        PostIngredientSummary(**summary_data)

        # RETURN
        return jsonify('success'), 200

    if version == 1:
        # CREATE: llm instance
        CLASS_INSTANCE_ChatOpenAI = LangChain_OpenAI_ChatOpenAI(
            model=model,
            temperature=0,
            max_tokens=None,
            # json_mode=True
            # logprobs=
            # stream_options=
        )

        # CONFIGURE: tools
        CLASS_INSTANCE_ChatOpenAI.bind_tools([
        # CLASS_INSTANCE_ChatOpenAI.llm.bind_tools([
        # CLASS_INSTANCE_ChatOpenAI.get_llm().bind_tools([
            # TODO: 
            #       - I want this WikipediaLoader Tool to update the "context" / "retriever" 
            #           that is then passed into the TOOL_RagChain to actually answer the question
            #       - I envision having many specific page loaders that I want to feed into the overall 
            #           context BEFORE the question is attempted to be answered
            TOOL_LangChain_WikipediaLoader,

            # TOOL_LangChain_PubMedLoader, 
            
            # TOOL_RagChain,
        ])
        # Debugging: Print bound tools
        print(f'DEBUG: Bound Tools: {CLASS_INSTANCE_ChatOpenAI.llm.tools}')  # Check if tools are bound


        # INVOKE: structured LLM w/ tools
        # 🚨 V1 - Not Calling Tools
        llm = CLASS_INSTANCE_ChatOpenAI.get_llm()
        result = llm.invoke(f"""
            Please summarize the following ingredient: {ingredient.name}. 
            First, use the WikipediaLoader tool to fetch information about the ingredient. 
            Then, based on that information, provide a summary and any potential health warnings.
        """)
        print(f'WHAT IS THE RESULT\n{result}')
        print(f'WHAT ARE THE TOOL CALLS\n{result.tool_calls}') ## TODO: there are none!

        # UPDATE > ingredient summary
        summary_data = {
            'ingredient_id': int(id),
            'summary': result.content, 
            'model': model,
            'sources': ['toolchain:', 'wikipedia']
        }
        if hasattr(result, 'warnings'):
            if result.warnings:
                summary_data['warnings'] = result.warnings

        PostIngredientSummary(**summary_data)

        # RETURN
        return jsonify('success'), 200