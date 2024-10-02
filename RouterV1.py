# IMPORTS > api server
from flask import Blueprint, jsonify, request

# IMPORTS > routes
from Ingredients.RouterV1 import v1_ingredients_blueprint
from Summaries.RouterV1 import v1_summaries_blueprint
from Products.RouterV1 import v1_products_blueprint

# CREATE > router
ROUTER_V1 = Blueprint('ROUTER_V1', __name__)

# REGISTER > Products blueprint
ROUTER_V1.register_blueprint(v1_products_blueprint)

# REGISTER > Ingredients blueprint
ROUTER_V1.register_blueprint(v1_ingredients_blueprint)

# REGISTER > Summaries blueprint
ROUTER_V1.register_blueprint(v1_summaries_blueprint)