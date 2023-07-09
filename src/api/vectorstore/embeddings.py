from dotenv import load_dotenv

from langchain.embeddings import SentenceTransformerEmbeddings


class Embeddings():
    def __init__(self):
        pass

    def SentenceTransformerEmbeddings(self):
        embeddings = SentenceTransformerEmbeddings(
            model_name="sentence-transformers/paraphrase-MiniLM-L6-v2",
        )
