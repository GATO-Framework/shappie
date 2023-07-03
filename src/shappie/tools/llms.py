import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from langchain import OpenAI

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


class LLMS:
    def __init__(self):
        pass

    def open_llm(self, model_id="gpt-3.5-turbo"):
        """
        Initializes and returns an instance of the OpenAI class.

        Parameters:
            model_id (str): The ID of the model to be used (default is "gpt-3.5-turbo").

        Returns:
            OpenAI: An instance of the OpenAI class.
        """
        return OpenAI(openai_api_key=openai_api_key, model=model_id)
