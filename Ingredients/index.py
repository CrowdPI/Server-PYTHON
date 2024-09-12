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
from langchain.document_loaders import WikipediaLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.runnables import RunnablePassthrough
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from typing import Optional
# IMPORT > LLMs > CREATE_langchain_openai_ChatOpenAI function
from utils.langchain_openai_ChatOpenAI import CREATE_langchain_openai_ChatOpenAI

ingredients_blueprint = Blueprint('ingredients', __name__)

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

class ChatOpenAI_Summary(BaseModel):
    """
    Summarize a specified dietary ingredient.
    """

    summary: str = Field(description="The summary of the specified dietary ingredient.")
    warnings: str = Field(description="A highlight of any potential health risks associated with the specified dietary ingredient.")
    health_rating: Optional[int] = Field(description="based on the specified dietary ingredients summary & warnings rank how healthy the ingredient is to consume from a 1 to 10 scale.")
    modified_rating: Optional[int] = Field(description="based on the specified dietary ingredients summary & warnings rank how healthy the ingredient is to consume from a scale of [1,2,3,4,5,6,8,9,10] (you cannot pick 7).")

@ingredients_blueprint.route('/ingredients/<id>/summarize', methods=['PUT']) # TODO: add a query param for model and set default to "gpt-4o"
def summarize_ingredient(id):
    # EXTRACT: model from query
    model = request.args.get('model', 'gpt-4o')
    print(f'THE MODEL\n{model}')

    # FETCH: ingredient from database
    ingredient = session.query(Ingredient).get(int(id))
    if ingredient is None:
        return jsonify({"error": "Ingredient not found"}), 204

    # CREATE: llm instance
    llm = CREATE_langchain_openai_ChatOpenAI(
        model=model,
        temperature=0,
        max_tokens=None,
        json_mode=True
        # logprobs=
        # stream_options=
    )

    print(f'🔎 THE LLM\n{llm}')
    print(f'\t1 - THE LLM client\n\t\t{llm.client}')
    print(f'\t2 - THE LLM async_client\n\t\t{llm.async_client}')
    print(f'\t3 - THE LLM root_client\n\t\t{llm.root_client}')
    print(f'\t4 - THE LLM root_async_client\n\t\t{llm.root_async_client}')
    print(f'\t5 - THE LLM model_name\n\t\t{llm.model_name}')
    print(f'\t6 - THE LLM openai_api_key\n\t\t{llm.openai_api_key}')
    print(f'\t7 - THE LLM openai_proxy\n\t\t{llm.openai_proxy}')

    # CREATE: structured llm instance
    structured_llm = llm.with_structured_output(ChatOpenAI_Summary)

    #############################################
    # Summarize Ingredient (V1 - Simple Prompt) #
    #############################################
    # CONFIGURE: prompt
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
    print(f'WHAT IS THE MESSAGE\n{messages}')
    result = structured_llm.invoke(messages)
    print(f'THE RESULT {result}')
    print(f'\t1 - THE RESULT.summary\n\t\t{result.summary}')
    print(f'\t2 - THE RESULT.warnings\n\t\t{result.warnings}')
    print(f'\t3 - THE RESULT.health_rating\n\t\t{result.health_rating}')
    print(f'\t4 - THE RESULT.modified_rating\n\t\t{result.modified_rating}')

    ###############################
    # UPDATE > ingredient summary #
    ###############################
    summary_text = result.summary
    new_summary = Summary(
        ingredient_id=int(id),
        text=summary_text,
        warnings=result.warnings,
        model=model
    )
    session.add(new_summary)
    session.commit()

    ##########
    # RETURN #
    ##########
    return jsonify('success'), 200

@ingredients_blueprint.route('/ingredients/<id>/summarize/source/<source>', methods=['PUT'])
def summarize_ingredient_wikipedia(id, source):
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

    # CREATE: llm instance
    llm = CREATE_langchain_openai_ChatOpenAI(
        model=model,
        temperature=0,
        max_tokens=None,
        json_mode=True
        # logprobs=
        # stream_options=
    )

    # CREATE: structured llm instance
    structured_llm = llm.with_structured_output(ChatOpenAI_Summary)

    ##########################
    # PROCESS WIKIPEDIA PAGE #
    ##########################
    # LOADER
    loader = WikipediaLoader(query=ingredient.name, load_max_docs=1)
    # loader = WikipediaLoader(query="NASCAR", load_max_docs=1) # intentionally break the context
    
    # DOCUMENTS
    documents = loader.load()
    print(f'THE DOCUMENTS\n{documents}')

    # TEXT-SPLITTER
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    print(f'THE TEXT SPLITTER\n{text_splitter}')

    # DOCUMENT CHUNKS
    chunks = text_splitter.split_documents(documents)
    print(f'THE CHUNKS\n{chunks}\n')

    # VECTORSTORE
    vectorstore = Chroma.from_documents(documents=chunks, embedding=OpenAIEmbeddings())
    print(f'THE VECTOR STORE\n{vectorstore}\n')

    # RETRIEVER
    retriever = vectorstore.as_retriever()
    print(f'THE RETRIEVER\n{retriever}\n')

    # PROMPT
    prompt_template = PromptTemplate.from_template("""
        You are a nutritionist AI that is tasked with providing a facts based summary of a provided Wikipedia webpage. 
        Focus your response on the nutritional aspects of the Wikipedia webpage.

        Do not mention who or what you are in your summarization. 

        Context: {context}
    """)

    # RAG CHAIN
    rag_chain = (
        {
            "context": retriever | format_docs, 
            "question": RunnablePassthrough()
        }
        | prompt_template
        | structured_llm
    )
    print(f'THE RAG CHAIN\n{rag_chain}\n')

    ################
    # 🎉 RESULT 🎉 #
    ################
    result = rag_chain.invoke(f"""
        Please summarize the following cooking ingredient:
    """)
    print(f'🎉 THE RESULT\n{result}')
    print(f'\t1 - THE RESULT.summary\n\t\t{result.summary}')
    print(f'\t2 - THE RESULT.warnings\n\t\t{result.warnings}')
    print(f'\t3 - THE RESULT.health_rating\n\t\t{result.health_rating}')
    print(f'\t4 - THE RESULT.modified_rating\n\t\t{result.modified_rating}')

    ###############################
    # UPDATE > ingredient summary #
    ###############################
    summary_text = result.summary
    new_summary = Summary(
        ingredient_id=int(id),
        text=summary_text,
        warnings=result.warnings,
        model=model
    )
    session.add(new_summary)
    session.commit()

    # Placeholder return statement
    return jsonify('success'), 200

    
