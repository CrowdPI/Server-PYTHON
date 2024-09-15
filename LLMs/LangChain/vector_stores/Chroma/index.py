from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

class LangChain_Chroma:
    def __init__(
        self,
        documents,
        embedding=OpenAIEmbeddings(),
        type='from_documents'
    ):
        self.documents=documents
        self.embedding=embedding
        self.type=type
        self.vectorstore=self._createChroma()

    def _createChroma(self):
        if (self.type == 'from_documents'):
            return self._fromDocuments()
    
    def _fromDocuments(self):
        return Chroma.from_documents(
            documents=self.documents,
            embedding=self.embedding
        )
