# IMPORTS
import os
from flask import Blueprint, jsonify

# IMPORTS > database
from models import Ingredient
from models import Summary
from database import db
from sqlAlchemy import session 

# IMPORTS > LLMs
import openai
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from langchain_openai import ChatOpenAI

ingredients_blueprint = Blueprint('ingredients', __name__)

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
@ingredients_blueprint.route('/ingredients/<id>/summarize', methods=['PUT'])
# @traceable # TODO:    i need to add this tracable decorator but it is not pushing anything to langsmith
#                       i _think_ i need to further extract / separate the flask route from the underlying function
#                       and then only trace the function?    
def summarize_ingredient(id):
    llm = ChatOpenAI()

    # Query the database for a single ingredient by ID
    ingredient = session.query(Ingredient).get(int(id))
    
    # Check if the ingredient exists
    if ingredient is None:
        return jsonify({"error": "Ingredient not found"}), 204

    #############################################
    # Summarize Ingredient (V1 - Simple Prompt) #
    #############################################
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

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
        text=summary_text
    )
    session.add(new_summary)
    session.commit()

    ##########
    # RETURN #
    ##########
    return jsonify(summary_text), 200