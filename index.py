import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# CONSTS
from consts.ingredients import INGREDIENTS
from version import CHANGE_LOG

server = Flask(__name__)
CORS(server, resources={r"/*": {"origins": "*"}})  # Allow all origins
# CORS(server, resources={r"/*": {"origins": ["...","..."]}})  # Allow all origins

@server.route('/', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, World! Time for Pie 🥧"})

@server.route('/changelog', methods=['GET'])
def get_changelog():
    return jsonify({"changelog": CHANGE_LOG}), 200

@server.route('/ingredients/<id>', methods=['GET'])
def get_ingredient(id):
    # EXTRACT : variables from request
    update_ingredient_summary = request.args.get('update_ingredient_summary')

    # FIND : ingredient from INGREDIENTS list
    ingredient = next((ing for ing in INGREDIENTS if ing['id'] == id), None)
    if ingredient is None:
        return jsonify({"error": "Ingredient not found"}), 204

    # TODO: UPDATE : ingredient summary based on query param conditional
    if update_ingredient_summary:
        pass

    return jsonify(ingredient), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server.run(host='0.0.0.0', port=port, debug=True)
