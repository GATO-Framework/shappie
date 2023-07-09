import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.vectorstores import Chroma
from src.api.vectorstore.splitters import Splitters
from src.api.vectorstore.loaders import Loaders
from src.api.vectorstore.embeddings import Embeddings


class ChromaDB:
    def __init__(self):
        self.embeddings = Embeddings().embeddings
        self.splitters = Splitters()
        self.loaders = Loaders()
        self.persistent_directory = "src/api/vectorstore/docs/chromadb"
        self.vectordb = Chroma(
            persist_directory=self.persistent_directory,
            embedding_function=self.embeddings,
        )

    def add_text_document(self, file_path, collection_name="text_documents"):
        try:
            text_loader = Loaders.text_loader(file_path=file_path)
            documents = text_loader.load()
            text_splitter = self.splitters.character_text_splitter()
            docs = text_splitter.split_documents(documents)
            self.db = self.chroma.from_documents(
                documents=docs,
                embedding=self.embeddings,
                persist_directory=self.persistent_directory,
                collection_name=collection_name,
            )
            return "Embeddings added to db"
        except Exception as e:
            return f"Error: {e} - Documents not loaded"

    def add_pdf_document(self, file_path, collection_name="pdf_documents"):
        try:
            pdf_loader = Loaders.pdf_loader(file_path=file_path)
            documents = pdf_loader.load_documents()
            text_splitter = self.splitters.recursive_text_splitter()
            docs = text_splitter.split_documents(documents)
            self.db = self.chroma.from_documents(
                documents=docs,
                embedding=self.embeddings,
                persist_directory=self.persistent_directory,
                collection_name=collection_name,
            )
            return "Embeddings added to db"
        except Exception as e:
            return f"Error: {e} - Documents not loaded"

    def retrive_documents(self, query, search_type: str = "similarity"):
        try:
            retriver = self.db.as_retriever(search_type=search_type)
            return retriver.get_relevant_documents(query=query)
        except Exception as e:
            return f"Error: {e} - Failed to retrieve documents"
