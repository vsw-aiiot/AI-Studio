from fastapi import APIRouter
from .generator import generate_docx

router = APIRouter()

@router.post("/doc/generate")
def generate_doc(text: str):
    file_path = generate_docx(text)
    return {"file": str(file_path)}