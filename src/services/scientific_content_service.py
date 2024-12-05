from langchain.document_loaders import ArxivLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQAWithSourcesChain
from typing import List, Dict
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.llms import HuggingFaceHub

def filter_complex_metadata(metadata: Dict) -> Dict:
    """Filter out None values and complex types from metadata."""
    filtered_metadata = {}
    for key, value in metadata.items():
        # Only keep simple types that Chroma accepts
        if isinstance(value, (str, int, float, bool)) and value is not None:
            filtered_metadata[key] = value
    return filtered_metadata

class ScientificContentService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScientificContentService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, api_token: str = None):  # Modificado para aceptar el token
        if not self.initialized:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            # LLM initialization with API token
            self.llm = HuggingFaceHub(
                repo_id="bigscience/bloom",
                huggingfacehub_api_token=api_token,  # Usar el token aquí
                model_kwargs={"temperature": 0.3}
            )
            self.initialized = True
        
    def fetch_arxiv_papers(self, query: str, max_papers: int = 5) -> List[Document]:
        """Fetch papers from ArXiv and clean their metadata."""
        loader = ArxivLoader(
            query=query,
            load_max_docs=max_papers,
            load_all_available_meta=True
        )
        documents = loader.load()
        
        # Clean up metadata for each document
        cleaned_documents = []
        for doc in documents:
            cleaned_metadata = filter_complex_metadata(doc.metadata)
            cleaned_doc = Document(
                page_content=doc.page_content,
                metadata=cleaned_metadata
            )
            cleaned_documents.append(cleaned_doc)
            
        return cleaned_documents
        
    def process_documents(self, documents: List[Document]):
        """Process documents and create a vector store."""
        # Split documents into chunks
        texts = self.text_splitter.split_documents(documents)
        
        # Ensure all document chunks have clean metadata
        cleaned_texts = []
        for text in texts:
            cleaned_metadata = filter_complex_metadata(text.metadata)
            cleaned_text = Document(
                page_content=text.page_content,
                metadata=cleaned_metadata
            )
            cleaned_texts.append(cleaned_text)
        
        # Create vector store with cleaned documents
        vectorstore = Chroma.from_documents(
            documents=cleaned_texts,
            embedding=self.embeddings
        )
        
        return vectorstore
        
    def generate_content(self, query: str, vectorstore) -> Dict[str, str]:
        """Generate content based on the query and vector store."""
        # Create retrieval chain
        qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        )
        
        # Generate response
        response = qa_chain({"question": query})
        return response