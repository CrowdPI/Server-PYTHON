CHANGE_LOG = [
    {
        "version": "0.0.8",
        "date": "10-1-2024",
        "changes": [
            "Removed all old code versions. Prepping for official push knowing Chains / Agents / Graphs",
        ]
    },
    {
        "version": "0.0.7",
        "date": "09-16-2024",
        "changes": [
            "Moved /products route to appropriate directory w/ blueprint",
            "ROUTE (GET): /products/<product_id>",
            "ROUTE (POST): /products/<product_id>/upload-img => local server file storage => no processing yet"
        ]
    },
    {
        "version": "0.0.6",
        "date": "09-16-2024",
        "changes": [
            "Removed the 'structured response' (summary & warnings) requirement from the /toolchain route. Still not calling tools",
            "Added 'version=2' to /toolchain route that is NOT using the extracted class. Tools are being called but no actual response",
            "Added summarization Agent",
        ]
    },
    {
        "version": "0.0.5",
        "date": "09-15-2024",
        "changes": [
            "Extracted underling function calls to their respective directories / classes",
            "V1 Attempt (not working) at tool-calls & rag chain combination",
            "Added LangChain PubMedLoader"
        ]
    },
    {
        "version": "0.0.4",
        "date": "09-11-2024",
        "changes": [
            "Added summaries.wikipedia column to postgres database",
            "Added summaries.model column to postgres database",
            "ROUTE (PUT): /ingredients/<id>/summarize/source/<source>. Currently only summarizing the stored wikipedia page for a passed ingredient id",
            "Extract & Improved the use of LancChain > OpenAI > ChatOpenAI w/ JSON structure",
        ]
    },
    {
        "version": "0.0.3",
        "date": "09-10-2024",
        "changes": [
            "Set Postgres timezone to UTC",
            "Added SUMMARIES table",
            "Upsert Ingredient Summary - V1 Simple Prompt w/ LangChain Tracing",
            "Get Ingredient Summaries."
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

__version__ = CHANGE_LOG[0]["version"]