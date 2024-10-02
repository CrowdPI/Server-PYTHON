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

# IMPORT > models
from Ingredients.models.PostIngredientSummary import PostIngredientSummary

####################
# HELPER FUNCTIONS #
####################
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# CREATE > subrouter
v1_ingredients_blueprint = Blueprint('ingredients', __name__)

@v1_ingredients_blueprint.route('/ingredients', methods=["GET"])
def get_ingredients():
    ingredients = session.query(Ingredient).order_by(Ingredient.name.asc()).all()
    return jsonify([{
        "id": ing.id,
        "name": ing.name,
        "alias": ing.alias
    } for ing in ingredients]), 200

@v1_ingredients_blueprint.route('/ingredients/<id>', methods=['GET'])
def get_ingredient(id):
    ingredient = session.query(Ingredient).get(int(id))
    if ingredient is None:
        return jsonify({"error": "Ingredient not found"}), 204
    return jsonify({
        "id": ingredient.id,
        "name": ingredient.name,
        "alias": ingredient.alias
    }), 200