# DOCS: https://python.langchain.com/v0.2/docs/integrations/document_loaders/wikipedia/

from langchain_community.document_loaders import WikipediaLoader

class LangChain_WikipediaLoader:
    def __init__(self, query, load_max_docs=1):
        self.query = query
        self.load_max_docs = load_max_docs
        self.document_loader = self._create_loader()
    
    def _create_loader(self):
        return WikipediaLoader(
            query=self.query, 
            load_max_docs=self.load_max_docs
        )
    
    def get_loader(self):
        return self.document_loader
    
    def call_loader(self):
        documents = self.document_loader.load()
        return documents
    
    def update_query(self, new_query):
        self.query = new_query
        self.document_loader = self._create_loader()