from langchain.document_loaders import ArxivLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQAWithSourcesChain
from typing import List, Dict

class ScientificContentService:
    def __init__(self, openai_api_key: str):
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
    def fetch_arxiv_papers(self, query: str, max_papers: int = 5) -> List[Dict]:
        loader = ArxivLoader(
            query=query,
            load_max_docs=max_papers,
            load_all_available_meta=True
        )
        documents = loader.load()
        return documents
        
    def process_documents(self, documents: List[Dict]):
        # Split documents into chunks
        texts = self.text_splitter.split_documents(documents)
        
        # Create vector store
        vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings
        )
        
        return vectorstore
        
    def generate_content(self, query: str, vectorstore) -> str:
        # Create retrieval chain
        qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        )
        
        # Generate response
        response = qa_chain({"question": query})
        return response