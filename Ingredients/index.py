# IMPORTS
import os
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
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import WikipediaLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser

ingredients_blueprint = Blueprint('ingredients', __name__)

####################
# HELPER FUNCTIONS #
####################
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@ingredients_blueprint.route('/ingredients', methods=["GET"])
def get_ingredients():
    ingredients = session.query(Ingredient).order_by(Ingredient.name.asc()).all()
    return jsonify([{"id": ing.id, "name": ing.name} for ing in ingredients]), 200

@ingredients_blueprint.route('/ingredients/<id>', methods=['GET'])
def get_ingredient(id):
    ingredient = session.query(Ingredient).get(int(id))
    if ingredient is None:
        return jsonify({"error": "Ingredient not found"}), 204
    return jsonify({"id": ingredient.id, "name": ingredient.name}), 200

# ROUTES > LLMs
# ROUTES > LLMs : summarize ingredient
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
    llm = ChatOpenAI(model=model)

    #############################################
    # Summarize Ingredient (V1 - Simple Prompt) #
    #############################################
    # CONFIGURE: single shot input
    input = f"""
        You are a nutritionist. Please summarize the following cooking ingredient:
        {ingredient.name}
    """

    result = llm.invoke(input)
    # print(f'1 - THE RESULT {result}')
    # print(f'2 - THE RESULT.content {result.content}')
    # print(f'3 - THE RESULT.additional_kwargs {result.additional_kwargs}')
    # print(f'4 - THE RESULT.response_metadata {result.response_metadata}')
    # print(f'5 - THE RESULT.id {result.id}')
    # print(f'6 - THE RESULT.usage_metadata {result.usage_metadata}')

    ###############################
    # UPDATE > ingredient summary #
    ###############################
    summary_text = result.content
    new_summary = Summary(
        ingredient_id=int(id),
        text=summary_text,
        model=model
    )
    session.add(new_summary)
    session.commit()

    ##########
    # RETURN #
    ##########
    return jsonify(summary_text), 200

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
    llm = ChatOpenAI(model=model)

    ##########################
    # PROCESS WIKIPEDIA PAGE #
    ##########################
    # LOADER
    loader = WikipediaLoader(query=ingredient.name, load_max_docs=1)
    
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
        You are a nutritionist AI that is tasked with providing a facts based summary of a provided Wikipedia webpage. Do not mention who or what you are in your summarization. Focus your response on the nutritional aspects of the Wikipedia webpage.

        Context: {context}
    """)

    # RAG CHAIN
    rag_chain = (
        {
            "context": retriever | format_docs, 
            "question": RunnablePassthrough()
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )
    print(f'THE RAG CHAIN\n{rag_chain}\n')

    ################
    # 🎉 RESULT 🎉 #
    ################
    result = rag_chain.invoke(f"""
        Please summarize the following cooking ingredient:
    """)
    print(f'🎉 THE RESULT\n{result}')

        ###############################
    # UPDATE > ingredient summary #
    ###############################
    summary_text = result
    new_summary = Summary(
        ingredient_id=int(id),
        text=summary_text,
        model=model
    )
    session.add(new_summary)
    session.commit()

    # Placeholder return statement
    return jsonify(result), 200

    
