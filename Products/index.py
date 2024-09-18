# IMPORTS
import os
import json
import time  # Add this import at the top

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

@products_blueprint.route('/products/<product_id>/upload-img', methods=['POST'])
def upload_img(product_id):
    # Get the uploaded file from the request
    uploaded_file = request.files.get('image')
    print(f'UPLOADED FILE\n{uploaded_file}')
    
    if uploaded_file:
        # Format the filename
        timestamp = int(time.time())  # Get current timestamp
        filename = f"product_id:{product_id}_{timestamp}.jpg"  # Assuming the file is a JPEG
        upload_path = os.path.join('USER_PHOTO_UPLOADS', filename)  # Define the upload path
        
        # Save the file
        uploaded_file.save(upload_path)
        print(f'File saved: {upload_path}')
        return jsonify({"message": "Image uploaded successfully"}), 200
    
    return jsonify({"error": "No file uploaded"}), 400