# IMPORTS
import os
from flask import Blueprint, jsonify, request

# IMPORTS > database
from models import Ingredient
from models import Summary
from database import db
from sqlAlchemy import session 

# IMPORTS > routes
summaries_blueprint = Blueprint('summaries', __name__)

# IMPORTS > LangChain
from langchain import hub

# IMPORTS > agents
# IMPORTS > agents > LangChain
from langchain.agents import create_tool_calling_agent, AgentExecutor
# IMPORTS > prompts
# IMPORTS > prompts > LangChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# IMPORTS > llms
# IMPORTS > llms > LangChain
from LLMs.LangChain.OpenAI.ChatOpenAI import LangChain_OpenAI_ChatOpenAI
# IMPORTS > llms > tools > LangChain
from LLMs.LangChain.tools.LangChain_TavilySearchResults import TOOL_LangChain_WebSearch

# IMPORTS > tools
from tools.SaveSummary import TOOL_Database_SaveSummary

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

@summaries_blueprint.route('/summaries/ingredients/<id>/summarize/agent', methods=['PUT'])
def summarize_ingredient_agent(id):
    # EXTRACT: model from query
    model = request.args.get('model', 'gpt-4o')

    # Fetch ingredient from database
    ingredient = session.query(Ingredient).get(int(id))
    if (ingredient is None or ingredient.wikipedia is None):
        return jsonify({"error": "Ingredient or Wikipedia page not found"}), 204

    # CREATE: structured llm instanceq
    CLASS_INSTANCE_ChatOpenAI = LangChain_OpenAI_ChatOpenAI(
        model=model,
        temperature=0,
        max_tokens=None,
        json_mode=True
        # logprobs=
        # stream_options=
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system", 
                "You are research assistant specializing in dietary nutrition & human biology."
            ),
            (
                "user", 
                "{input}"
            ),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # CONFIGURE: tools
    # prompt = hub.pull("hwchase17/openai-functions-agent") # what is this?
    tools = [
        TOOL_LangChain_WebSearch,
        TOOL_Database_SaveSummary,
        # write_report, 
        # save_to_file
    ]
    llm_with_tools = CLASS_INSTANCE_ChatOpenAI.llm.bind_tools(tools)

    # CONFIGURE: agent
    agent = create_tool_calling_agent(
        llm_with_tools, 
        tools, 
        prompt
    )

    # The agent executor is the runtime for an agent.
    # This is what actually calls the agent, executes the actions it chooses, passes the action outputs back to the agent, and repeats.
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True
    )

    # `list` allows the agent's content to stream to the terminal
    list(agent_executor.stream({
        "input": f"""
            A)
                You are a nutritionist AI agent tasked with providing a facts based research for: 
                    ingredient name: {ingredient.name}
                    ingredient id: {ingredient.id}

                You must return 2 different items. 

                1. summary (required): a summarization of the collective research you can collect on {ingredient.name} across all available tools. 

                2. warnings (optional): a summarization of any nutritional or health risks associated with {ingredient.name}
                
                Do not mention who or what you are in any of your your summarizations.

            B) 
                Once you have the required summary and the optional warnings then save the summary for {ingredient.id} to the database using the TOOL_Database_SaveSummary tool.

                The arguments for this tool are:
                    ingredient_id: {ingredient.id}, 
                    model: {model}, 
                    summary: <your summary>,
                    warnings: <your warnings>,
        """, 
        "agent_scratchpad": ""
    }))

    print(f'THE AGENT EXECUTOR', agent_executor)

    return 'success', 200