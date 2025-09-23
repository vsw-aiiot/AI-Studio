import os
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
# from langchain.document_loaders import TextLoader, PDFPlumberLoader, Docx2txtLoader, UnstructuredMarkdownLoader
from langchain_community.document_loaders import (
    TextLoader,
    PDFPlumberLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader,
)

INGEST_DIR = "rag/documents"
CHROMA_DB_DIR = "rag/chroma_db"

# Pick embedding model (lightweight but good)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def load_documents() -> List[str]:
    docs = []
    for fname in os.listdir(INGEST_DIR):
        fpath = os.path.join(INGEST_DIR, fname)
        if fname.endswith(".txt"):
            docs.extend(TextLoader(fpath).load())
        elif fname.endswith(".md"):
            docs.extend(UnstructuredMarkdownLoader(fpath).load())
        elif fname.endswith(".pdf"):
            docs.extend(PDFPlumberLoader(fpath).load())
        elif fname.endswith(".docx"):
            docs.extend(Docx2txtLoader(fpath).load())
    return docs

def ingest():
    print("🔍 Loading and chunking documents...")
    raw_docs = load_documents()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(raw_docs)

    print(f"✅ Total Chunks: {len(chunks)}")
    print("📦 Creating Chroma DB...")
    vectorstore = Chroma.from_documents(chunks, embedding=embedding_model, persist_directory=CHROMA_DB_DIR)
    vectorstore.persist()
    print("🚀 Ingestion completed and saved to DB.")

# if __name__ == "__main__":
#     ingest()
