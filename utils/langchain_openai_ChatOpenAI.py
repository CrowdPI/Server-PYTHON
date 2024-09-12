from langchain_openai import ChatOpenAI # DOCS: https://api.python.langchain.com/en/latest/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html#langchain_openai.chat_models.base.ChatOpenAI

def CREATE_langchain_openai_ChatOpenAI(model='gpt-4o', temperature=0, max_tokens=None, json_mode=None):
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        # logprobs=
        # stream_options=
    )

    if json_mode:
        return llm.bind(response_format={"type": "json_object"})
    
    return llm