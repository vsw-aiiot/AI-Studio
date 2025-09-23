from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
import os

CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), "db")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_vector_store():
    return Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)
