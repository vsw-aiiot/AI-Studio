from fastapi import APIRouter

from .retriever import retrieve_documents
from .ingestor import ingest
from .vector_store import get_vector_store


router = APIRouter()

@router.post("/rag/ingest")
def ingest_doc(path: str):
    ingest()
    return {"status": "ingested"}

@router.get("/rag/retrieve")
def retrieve(query: str):
    chunks = retrieve_documents(query)
    return {"chunks": chunks}