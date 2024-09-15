# DOCS: https://api.python.langchain.com/en/latest/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html#langchain_openai.chat_models.base.ChatOpenAI
from langchain_openai import ChatOpenAI

class LangChain_OpenAI_ChatOpenAI:
    def __init__(
        self, 
        model='gpt-4', 
        temperature=0, 
        max_tokens=None, 
        json_mode=None
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.json_mode = json_mode
        self.llm = self._create_llm()

    def _create_llm(self):
        llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            # logprobs=
            # stream_options=
        )
        if self.json_mode:
            return llm.bind(response_format={"type": "json_object"})
        return llm

    def get_llm(self):
        return self.llm