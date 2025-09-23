from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

CHROMA_DB_DIR = "rag/chroma_db"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load embeddings and vector store
embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embedding)

def retrieve_documents(query: str, top_k: int = 4) -> list[str]:
    """
    Retrieve top_k relevant document chunks using vector similarity search.
    """
    results = vectorstore.similarity_search(query, k=top_k)
    return [doc.page_content for doc in results]

# Test retrieval (optional)
if __name__ == "__main__":
    q = input("Enter a question: ")
    docs = retrieve_documents(q)
    print("\nTop Matches:")
    for i, d in enumerate(docs, 1):
        print(f"{i}. {d}\n")
