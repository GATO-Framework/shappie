import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from src.api.vectorstore.loaders import Loaders
from src.api.vectorstore.splitters import Splitters
from src.api.vectorstore.embeddings import Embeddings
from src.api.vectorstore.chroma import Chroma

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

class WebScraper:
    def __init__(self):
        self.loaders = Loaders()
        self.splitters = Splitters()
        self.embeddings = Embeddings()
        self.chromadb = Chroma()

    def get_page_data(self, links):
        for link in links:
            target_site = [link]
            loader = self.loaders.html_loader(urls=target_site)
            data = loader.load()
            docs = self.split_data(data)
            self.store_data(data=docs, collection_name=target_site)
            return f"Embedding from {link} added to db"

    def split_data(self, data):
        splitter = self.splitters(chunk_size=200, chunk_overlap=20)
        return splitter.split_documents(data)

    def store_data(self, data, collection_name="text_documents"):
        self.chromadb.from_documents(
            documents=data,
            embedding=self.embeddings,
            persist_directory=self.chromadb.persistent_directory,
            collection_name=collection_name,
        )
        return "Embeddings added to db"
