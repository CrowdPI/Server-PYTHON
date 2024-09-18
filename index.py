# IMPORTS
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify

# IMPORTS > routes
from Ingredients.index import ingredients_blueprint
from Summaries.index import summaries_blueprint
from Products.index import products_blueprint

# IMPORTS > SQLAlchemy
from sqlAlchemy import session

# IMPORTS > database
from database import db
 
# IMPORTS > cors
from flask_cors import CORS

# IMPORTS > models
from models import Product

# IMPORTS > consts
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

@server.route('/', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, World! Time for Pie 🥧"})

@server.route('/changelog', methods=['GET'])
def get_changelog():
    return jsonify({"changelog": CHANGE_LOG}), 200

# REGISTER > Products blueprint
server.register_blueprint(products_blueprint)

# REGISTER > Ingredients blueprint
server.register_blueprint(ingredients_blueprint)

# REGISTER > Summaries blueprint
server.register_blueprint(summaries_blueprint)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server.run(host='0.0.0.0', port=port, debug=True)
