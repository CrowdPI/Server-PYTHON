# IMPORTS
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify

# IMPORTS > routes
from RouterV1 import ROUTER_V1

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

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
print(f'WHAT IS THIS OPEN API KEY {OPENAI_API_KEY}')

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

server.register_blueprint(ROUTER_V1)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server.run(host='0.0.0.0', port=port, debug=True)
