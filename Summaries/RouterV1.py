# IMPORTS
import os
from flask import Blueprint, jsonify, request

# IMPORTS > database
from models import Ingredient
from models import Summary
from database import db
from sqlAlchemy import session 

# IMPORTS > routes
v1_summaries_blueprint = Blueprint('summaries', __name__)

# IMPORTS > LangChain
from langchain import hub

# IMPORTS > agents
# IMPORTS > agents > LangChain
from langchain.agents import create_tool_calling_agent, AgentExecutor
# IMPORTS > prompts
# IMPORTS > prompts > LangChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# IMPORTS > llms
# IMPORTS > llms > LangChain
from LLMs.LangChain.OpenAI.ChatOpenAI import LangChain_OpenAI_ChatOpenAI
# IMPORTS > llms > tools > LangChain
from LLMs.LangChain.tools.LangChain_TavilySearchResults import TOOL_LangChain_WebSearch

# IMPORTS > tools
from tools.SaveSummary import TOOL_Database_SaveSummary

@v1_summaries_blueprint.route('/summaries/ingredients/<id>', methods=["GET"])
def get_ingredient_summaries(id):
    # TODO: get all the summaries.ingredient_id === <id> from the param
    summaries = session.query(Summary).filter(Summary.ingredient_id == int(id)).order_by(Summary.created_at.desc()).all()

    if summaries is None:
        return jsonify([]), 200  # Return an empty array with 200 OK status
    else :
        result = jsonify([{
            "id": ing.id, 
            "text": ing.text, 
            "warnings": ing.warnings,
            "model": ing.model,
            "sources": ing.sources,
            "created_at": ing.created_at, 
        } for ing in summaries])
        return result, 200