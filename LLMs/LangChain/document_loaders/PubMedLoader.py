# DOCS: https://python.langchain.com/v0.2/docs/integrations/document_loaders/pubmed/

from langchain_community.document_loaders import PubMedLoader

class LangChain_PubMedLoader:
    def __init__(self, query):
        self.query = query
        self.docs = None
        self.instance = self._create()

    def _create(self):
        return PubMedLoader(self.query) 

    def load(self):
        self.docs = self.instance.load()
        return self.docs

    def getDocs(self):
        return self.docs
