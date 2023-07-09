from langchain.retrievers import SelfQueryRetriever
from src.api.vectorstore.embeddings import Embeddings
from src.api.vectorstore.chroma import ChromaDB
from src.shappie.tools.llms import LLMS


class VectorStoreRetrievers:
    def __init__(self):
        self.embeddings = Embeddings().openai_embeddings()
        self.vectordb = ChromaDB().persistent_directory
        self.llm = LLMS().open_llm()

    def self_querying(self, query):
        retriever = SelfQueryRetriever.from_llm(
            self.llm,
            self.embeddings,
            self.vectordb,
            document_content_description="",
            metadata_field_info="",
            verbose=True,
        )
        documents = retriever.get_relevant_documents(query=query, k=5)
        return documents.page_contents
