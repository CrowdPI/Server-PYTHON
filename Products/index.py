# IMPORTS
import os
import json

# IMPORTS > database
from sqlAlchemy import session

# IMPORTS > models
from models import Product

# IMPORTS > flask app
from flask import Blueprint, jsonify, request

# CREATE > subrouter
products_blueprint = Blueprint('products', __name__)

# ROUTES > Products
@products_blueprint.route('/products', methods=["GET"])
def get_products():
    products = session.query(Product).order_by(Product.name.asc()).all()
    return jsonify([{"id": ing.id,"brand_name": ing.brand_name, "name": ing.name} for ing in products]), 200

@products_blueprint.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    ingredient = session.query(Product).get(int(product_id))
    if ingredient is None:
        return jsonify({"error": "Product not found"}), 204
    return jsonify({
        "id": ingredient.id,
        "brand_name": ingredient.brand_name or None,
        "name": ingredient.name,
    }), 200