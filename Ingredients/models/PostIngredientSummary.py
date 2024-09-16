# IMPORTS
# IMPORTS > database
from models import Summary
from sqlAlchemy import session 

def PostIngredientSummary(
    ingredient_id, 
    summary, 
    warnings, 
    model,
    sources,
):
    new_summary = Summary(
        ingredient_id=ingredient_id,
        text=summary,
        warnings=warnings,
        model=model,
        sources=sources
    )
    session.add(new_summary)
    session.commit()

    return ingredient_id