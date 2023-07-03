import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.vectorstores import Chroma
from src.api.vectorstore.splitters import Splitters
from src.api.vectorstore.loaders import Loaders
from src.api.vectorstore.embeddings import Embeddings


class ChromaDB:
    def __init__(self):
        """
        This is a class for a Chroma DB vector store.

        It allows for adding and retrieving documents to and from the database. Chroma is the library used for this,
        and it stores the vector store locally. The `persistent_directory` parameter ensures that Chroma saves
        the data to the vector store.

        This class uses OpenAI embeddings which have an associated API fee.

        Attributes:
            chroma (Chroma): An instance of the Chroma class.
            embeddings (Embeddings): An instance of the Embeddings class.
            splitters (Splitters): An instance of the Splitters class.
            loaders (Loaders): An instance of the Loaders class.
            persistent_directory (str): The directory where the vector store data is stored.
            vectordb (Chroma): An instance of the Chroma class with the specified parameters.
        """
        self.chroma = Chroma()
        self.embeddings = Embeddings().embeddings
        self.splitters = Splitters()
        self.loaders = Loaders()
        self.persistent_directory = "src/api/vectorstore/docs/chromadb"
        self.vectordb = Chroma(
            persist_directory=self.persistent_directory,
            embedding_function=self.embeddings,
        )

    def add_text_document(self, file_path, collection_name="text_documents"):
        """
        Adds a text document to the database.

        Args:
            file_path (str): The path to the text document.
            collection_name (str, optional): The name of the collection to store the document in. Defaults to "text_documents".

        Returns:
            str: A message indicating whether the embeddings were successfully added to the database or an error message if the documents failed to load.
        """
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
        """
        Add a PDF document to the collection.

        Args:
            file_path (str): The path to the PDF file.
            collection_name (str, optional): The name of the collection to add the document to. Defaults to "pdf_documents".

        Returns:
            str: A message indicating that the embeddings have been added to the database, or an error message if an exception occurs.
        """
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
        """
        Retrieve documents based on the given query.

        Parameters:
            query (str): The query string for retrieving documents.
            search_type (str): The type of search to perform. Defaults to "similarity".
                options are "similarity", "similarity_score_threshold", "mmr".

        Returns:
            list: A list of relevant documents.

        Raises:
            Exception: If an error occurs while retrieving documents.
        """
        try:
            retriver = self.db.as_retriever(search_type=search_type)
            return retriver.get_relevant_documents(query=query)
        except Exception as e:
            return f"Error: {e} - Failed to retrieve documents"


# TODO: Text mutable functionality

#    def add_mutable_document(self, page_content, document_id, page, collection_name="mutable_documents"):
#        document = Document(page_content=page_content, metadata={"page":page})
#        return self.db.from_documents(
#            documents =[document],
#            embedding=self.embeddings,
#            persist_directory=self.persistent_directory,
#            collection_name=collection_name,
#            ids=document_id
#            )
#
#    def update_mutable_document(self, page_content, document_id, page):
#        document = Document(page_content=page_content, metadata={"page":page})
#        return self.db.update_document(document, document_id)
#
