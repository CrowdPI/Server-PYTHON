# IMPORTS
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
# IMPORTS > database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import db 

# IMPORTS > cors
from flask_cors import CORS

# IMPORTS > models
from models import Ingredient
from models import Product

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server.run(host='0.0.0.0', port=port, debug=True)
