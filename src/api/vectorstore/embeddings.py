import os
from dotenv import load_dotenv

from langchain.embeddings import OpenAIEmbeddings

load_dotenv()

class Embeddings():
    def __init__(self):
        pass

    def openai_embeddings(self):
        """
        Get the OpenAI embeddings.

        :return: The OpenAI embeddings.
        """
        return OpenAIEmbeddings()