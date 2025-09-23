from fastapi import APIRouter
from .convert import convert_to_markdown

router = APIRouter()

@router.post("/markdown/convert")
def convert_md(markdown_text: str):
    html = convert_to_markdown(markdown_text)
    return {"html": html}
    
    