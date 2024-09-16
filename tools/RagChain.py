from langchain_core.tools import tool

from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate

####################
# HELPER FUNCTIONS #
####################
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@tool
def TOOL_RagChain(prompt, retriever, llm):
    """
        Function to process the retriever information w/ tools
    """
    # CONFIGURE: prompt
    prompt_template = PromptTemplate.from_template("""
        {prompt} 

        Context: {context}
    """)
    # print(f'THE PROMPT TEMPLATE\n{prompt_template}')

        # CONFIGURE: rag chain
    rag_chain = (
        {
            "context": retriever | format_docs, 
            "question": RunnablePassthrough()
        }
        | prompt_template
        | llm
    )
    # print(f'THE RAG CHAIN\n{rag_chain}\n')

    # INVOKE: rag chain
    result = rag_chain.invoke(f"""
        Please summarize the following cooking ingredient:
    """)
    print(f'🎉 THE RESULT\n{result}')

    return result