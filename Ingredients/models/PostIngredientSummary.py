# IMPORTS
# IMPORTS > database
from models import Summary
from sqlAlchemy import session 

def PostIngredientSummary(ingredient_id, summary, warnings, model):
    new_summary = Summary(
        ingredient_id=ingredient_id,
        text=summary,
        warnings=warnings,
        model=model
    )
    session.add(new_summary)
    session.commit()

    return ingredient_id