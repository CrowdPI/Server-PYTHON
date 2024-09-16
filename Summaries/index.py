# IMPORTS
import os
from flask import Blueprint, jsonify

# IMPORTS > database
from models import Ingredient
from models import Summary
from database import db
from sqlAlchemy import session 

summaries_blueprint = Blueprint('summaries', __name__)

@summaries_blueprint.route('/summaries/ingredients/<id>', methods=["GET"])
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
