from langchain.text_splitter import RecursiveCharacterTextSplitter

class LangChain_RecursiveTextSplitter:
    def __init__(
        self, 
        chunk_size=1000, 
        chunk_overlap=200, 
        length_function=len,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function
        self.text_splitter = self._create_text_splitter()
        
    def _create_text_splitter(self):
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self.length_function,
        )
    
    def split_documents(self, documents):
        return self.text_splitter.split_documents(documents)