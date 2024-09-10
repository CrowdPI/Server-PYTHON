# IMPORTS
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify

# IMPORTS > LLMs
import openai
from langsmith.wrappers import wrap_openai
from langsmith import traceable

# IMPORTS > database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import db 

# IMPORTS > cors
from flask_cors import CORS

# IMPORTS > models
from models import Ingredient
from models import Product
from models import Summary

# IMPORTS > consts
from consts.ingredients import INGREDIENTS
from version import CHANGE_LOG

# LOAD > environment variables from .env file
load_dotenv()

# CREATE > server
server = Flask(__name__)

# CONFIGURE > server
# CONFIGURE > server : CORS
CORS(server, resources={r"/*": {"origins": "*"}})  # Allow all origins
# CORS(server, resources={r"/*": {"origins": ["...","..."]}})  # Allow all origins

# CONFIGURE > database
server.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('DATABASE_URL')
server.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {"options": "-c timezone=utc"}
}
db.init_app(server)

# CONFIGURE > SQLAlchemy enginer
engine = create_engine(
    os.getenv('DATABASE_URL'), 
    connect_args={"options": "-c timezone=utc"}
)
Session = sessionmaker(bind=engine)
session = Session()

@server.route('/', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, World! Time for Pie 🥧"})

@server.route('/changelog', methods=['GET'])
def get_changelog():
    return jsonify({"changelog": CHANGE_LOG}), 200

# ROUTES > Ingredients
@server.route('/products', methods=["GET"])
def get_products():
    products = session.query(Product).order_by(Product.name.asc()).all()
    return jsonify([{"id": ing.id,"brand_name": ing.brand_name, "name": ing.name} for ing in products]), 200

# ROUTES > Ingredients
@server.route('/ingredients', methods=["GET"])
def get_ingredients():
    ingredients = session.query(Ingredient).order_by(Ingredient.name.asc()).all()
    return jsonify([{"id": ing.id, "name": ing.name} for ing in ingredients]), 200

@server.route('/ingredients/<id>', methods=['GET'])
def get_ingredient(id):
    # Query the database for a single ingredient by ID
    ingredient = session.query(Ingredient).get(int(id))
    
    # Check if the ingredient exists
    if ingredient is None:
        return jsonify({"error": "Ingredient not found"}), 204

    # Convert the ingredient to a dictionary
    return jsonify({"id": ingredient.id, "name": ingredient.name}), 200

# ROUTES > LLMs
# ROUTES > LLMs : summarize ingredient
# Auto-trace LLM calls in-context
client = wrap_openai(openai.Client())

@traceable
@server.route('/ingredients/<id>/summarize', methods=['PUT'])
def summarize_ingredient(id):
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

    result = client.chat.completions.create(
        messages=[
            {"role": "user", "content": input}
        ],
        model="gpt-4o-mini"
    )

    ###############################
    # UPDATE > ingredient summary #
    ###############################
    summary_text = result.choices[0].message.content
    new_summary = Summary(
        ingredient_id=int(id),
        text=summary_text
    )
    session.add(new_summary)
    session.commit()

    ##########
    # RETURN #
    ##########
    print(f'THE NEW SUMMARY {new_summary}')
    print(f'V2 {summary_text}' )
    return jsonify(summary_text), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server.run(host='0.0.0.0', port=port, debug=True)
