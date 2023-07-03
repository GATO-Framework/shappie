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
    """
    A class for web scraping. Accepts html website links[]. This
    will grab the data and store it in the local vector store. Use
    the retrieve

    Attributes:
        loaders (Loaders): An instance of the Loaders class.
        splitters (Splitters): An instance of the Splitters class.
        embeddings (Embeddings): An instance of the Embeddings class.
        chromadb (Chroma): An instance of the Chroma class.
    """

    def __init__(self):
        self.loaders = Loaders()
        self.splitters = Splitters()
        self.embeddings = Embeddings()
        self.chromadb = Chroma()

    def get_page_data(self, links):
        """
        Retrieves page data from a list of links.

        Args:
            links: A list of links to retrieve data from.

        Returns:
            None
        """
        for link in links:
            target_site = [link]
            loader = self.loaders.html_loader(urls=target_site)
            data = loader.load()
            docs = self.split_data(data)
            self.store_data(data=docs, collection_name=target_site)
            return f"Embedding from {link} added to db"

    def split_data(self, data):
        """
        Splits the given data into chunks using a splitter.

        Parameters:
            data (any): The data to be split into chunks.

        Returns:
            any: The split data.
        """
        splitter = self.splitters(chunk_size=200, chunk_overlap=20)
        return splitter.split_documents(data)

    def store_data(self, data, collection_name="text_documents"):
        """
        Store data in the chromadb.

        Parameters:
            data (list): The data to be stored in the chromadb.
            collection_name (str): The name of the collection in which the data will be stored. Defaults to "text_documents".

        Returns:
            None
        """
        self.chromadb.from_documents(
            documents=data,
            embedding=self.embeddings,
            persist_directory=self.chromadb.persistent_directory,
            collection_name=collection_name,
        )
        return "Embeddings added to db"
