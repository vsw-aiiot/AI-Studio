from fastapi import APIRouter, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse

from tools.context_manager.context_operator import export_context, import_context

router = APIRouter()


@router.get("/context/export")
def export_context_route():
    return FileResponse("user_context.json", media_type="application/json", filename="context.json")


@router.post("/context/import")
def import_context_route(file: UploadFile = File(...)):
    result = import_context(file)
    return RedirectResponse(url="/?imported=true", status_code=303)


