__version__ = "0.0.3"

CHANGE_LOG = [
    {
        "version": "0.0.3",
        "date": "09-10-2024",
        "changes": [
            "Set Postgres timezone to UTC",
            "Added SUMMARIES table",
            "Upsert Ingredient Summary - V1 Simple Prompt w/ LangChain Tracing",
        ]
    },
    {
        "version": "0.0.2",
        "date": "09-09-2024",
        "changes": [
            "Updated README",
            "CORS",
            "Added LOCAL Postgres Database",
            "Added PRODUCTS / INGREDIENTS / PRODUCT_INGREDIENTS / INGREDIENTS_COMPONENTS tables"
        ]
    },
    {
        "version": "0.0.1",
        "date": "09-03-2024",
        "changes": [
            "Initial Commit",
            "Added Flask Server",
            "Added GET /ingredients/:id > endpoint to fetch ingredient from a preset fixed local list (no DB)",
        ]
    }
]