from langchain.tools import tool

# IMPORT > models
from Ingredients.models.PostIngredientSummary import PostIngredientSummary

@tool
def TOOL_Database_SaveSummary(
    ingredient_id: int, 
    summary: str,
    model: str, 
    warnings=None,
):
    """Adds a new ingredient summary to the postgres database"""
    if not ingredient_id or not summary or not model:
        print(f'--ERROR--\n\tMissing ingredient_id or summary or model')
        return False

    # UPDATE > ingredient summary
    summary_data = {
        'ingredient_id': ingredient_id,
        'summary': summary, 
        'model': model,
        'sources': ['agent:', 'AgentExecutor'] # TODO: this also need to be dyanmic
    }
    if warnings:
        summary_data['warnings'] = warnings

    PostIngredientSummary(**summary_data)