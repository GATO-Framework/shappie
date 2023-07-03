from langchain.document_loaders import TextLoader, PyPDFLoader, UnstructuredHTMLLoader

class Loaders():
    def __init__(self):
        pass

    def text_loader(self, file_path):
        """
        Loads a text file and returns a TextLoader object.

        Parameters:
            file_path (str): The path to the text file.

        Returns:
            TextLoader: The TextLoader object representing the loaded text file.

        Raises:
            ValueError: If file_path is empty or not a .txt file.
        """
        if not file_path:
            return "Error - Please select a file_path and pass it to this function."
        if not file_path.endswith(".txt"):
            return "Error - Please select another loader, only .txt files are supported."
        else:
            return TextLoader(file_path=file_path)


    def pdf_loader(self, file_path):
        """
        Load a PDF file and return a PyPDFLoader object.

        Parameters:
            file_path (str): The path to the PDF file.

        Returns:
            PyPDFLoader: A PyPDFLoader object representing the loaded PDF file.

        Raises:
            ValueError: If the `file_path` is empty or if it does not end with ".pdf".
        """
        if not file_path:
            return "Error - Please select a file_path and pass it to this function."
        if not file_path.endswith(".pdf"):
            return "Error - Please select another loader, only .pdf files are supported."
        else:
            return PyPDFLoader(file_path=file_path)

    def html_loader(self, file_path):
        """
        Loads an HTML file from the specified file path.

        Parameters:
            file_path (str): The path to the HTML file.

        Returns:
            UnstructuredHTMLLoader: An instance of the UnstructuredHTMLLoader class.

        Raises:
            ValueError: If the file_path is empty or None.
            ValueError: If the file_path does not end with ".html".
        """
        if not file_path:
            return "Error - Please select a file_path and pass it to this function."
        if not file_path.endswith(".html"):
            return "Error - Please select another loader, only .html files are supported."
        else:
            return UnstructuredHTMLLoader(file_path=file_path)