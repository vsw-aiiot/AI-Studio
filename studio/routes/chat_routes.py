from pathlib import Path
from typing import Dict, List

from fastapi import APIRouter, Depends, Form, Query, Request, HTTPException
from fastapi.params import Body
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime
import logging

from chat_client.generic_model_config import MODEL_REGISTRY, get_model_handler
from studio.services.db import get_session
from studio.services.crud import (
    create_conversation,
    get_conversation,
    get_conversations_by_user,
    update_conversation,
    append_message
)
from studio.services.models import Conversation

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

router = APIRouter()

# DEFAULT_MODEL_ID = next(iter(MODEL_REGISTRY.keys()))
DEFAULT_MODEL_ID = "mixtral"

# very simple in‑memory store (move to Redis/DB later)
conversations_store: Dict[str, List[Dict[str, str]]] = {}

logger = logging.getLogger(__name__)

# ---------- NEW: /chat entry ----------
@router.get("/", response_class=HTMLResponse)
async def chat_entry(request: Request):
    logger.info('[Guest Chat initiated]')
    if not request.session.get("user_id"):
        return templates.TemplateResponse(
            "chat_guest.html",
            {
                "request": request,
                "models": MODEL_REGISTRY,
                "DEFAULT_MODEL_ID": DEFAULT_MODEL_ID,  # FIX: Pass model id
            }
        )
    logger.info(f'[Chat initiated for]- {request.session.get("user_id")}')
    return RedirectResponse(url=f"/chat/model/{DEFAULT_MODEL_ID}", status_code=303)

# @router.get("/{model_id}", response_class=HTMLResponse)
async def get_chat_view(
    request: Request,
    model_id: str,
    conversation_id: int = Query(default=None),
    session_db: Session = Depends(get_session),
):
    logger.info(f'get_chat_view - Initiated')
    print(f"Model used: {model_id}")
    
    user_id = request.session.get("user_id")
    template = "chat_guest.html" if not user_id else "chat.html"

    conversation = None
    if user_id and conversation_id:
        conversation = get_conversation(session_db, conversation_id, user_id)
        print(f'retriving stored messages from conversation storage object==>{conversation.messages}')

    conversations_list = get_conversations_by_user(session_db, user_id) if user_id else []

    return templates.TemplateResponse(
        template,
        {
            "request": request,
            "agent": model_id,
            "DEFAULT_MODEL_ID": DEFAULT_MODEL_ID,
            "response": None,
            "user_input": None,
            "conversation": conversation.messages if conversation else [],
            "conversation_id": conversation.id if conversation else None,
            "conversations": conversations_list,
            "models": MODEL_REGISTRY,
        },
    )


# Model-based entry
@router.get("/model/{model_id}", response_class=HTMLResponse)
async def get_chat_view_model(
    request: Request,
    model_id: str,
    session_db: Session = Depends(get_session),
):
    logger.info(f'get_chat_view_model - Initiated')
    user_id = request.session.get("user_id")
    conversations_list = get_conversations_by_user(session_db, user_id) if user_id else []
    return templates.TemplateResponse(
        "chat.html" if user_id else "chat_guest.html",
        {
            "request": request,
            "agent": model_id,
            "conversation": [],
            "conversation_id": None,
            "conversations": conversations_list,
            "models": MODEL_REGISTRY,
        },
    )


# Conversation-based entry
@router.get("/conversation/{conversation_id}", response_class=HTMLResponse)
async def get_chat_view_conversation(
    request: Request,
    conversation_id: int,
    session_db: Session = Depends(get_session),
):
    logger.info(f'get_chat_view_conversation - Initiated')
    user_id = request.session.get("user_id")
    conversation = get_conversation(session_db, conversation_id, user_id)
    conversations_list = get_conversations_by_user(session_db, user_id) if user_id else []
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "agent": DEFAULT_MODEL_ID,
            "conversation": conversation.messages if conversation else [],
            "conversation_id": conversation.id if conversation else None,
            "conversations": conversations_list,
            "models": MODEL_REGISTRY,
        },
    )

# ---------- Guest chat ----------
# @router.post("/public/send")
# async def guest_chat_send(user_input: str = Form(...)):
#     logger.info(f'guest_chat_send - Initiated')
#     handler = get_model_handler(DEFAULT_MODEL_ID)
#     logger.info(f'handler - [Object accessing]=>{DEFAULT_MODEL_ID} - A hard coded default value')
#     if not handler:
#         return {"error": f"No handler found for model Default Model"}
#     ai_response = handler(user_input)
#     logger.info(f'AI Response as handled object generated')
#     logger.info(f'Returning user Input as =>\t{user_input}\nAI Response=>\t{ai_response}')
#     return {"user": user_input, "ai": ai_response}

# ---------- Guest chat entry ----------
@router.get("/public/", response_class=HTMLResponse)
async def guest_chat_page(request: Request):
    logger.info('[Guest Chat Page Initiated]')
    return templates.TemplateResponse(
        "chat_guest.html",
        {
            "request": request,
            "models": MODEL_REGISTRY,
            "DEFAULT_MODEL_ID": DEFAULT_MODEL_ID,
        },
    )

# ---------- Guest chat send ----------
@router.post("/public/send")
async def guest_chat_send(user_input: str = Form(...)):
    handler = get_model_handler(DEFAULT_MODEL_ID)
    if not handler:
        return {"error": f"No handler found for model Default Model"}
    ai_response = handler(user_input)
    return {"user": user_input, "ai": ai_response}



# ---------- Logged-in chat send ----------
@router.post("/model/{model_id}/send")
async def post_chat_message(
    request: Request,
    model_id: str,
    user_input: str = Form(...),
    conversation_id: int = Form(None),
    session_db: Session = Depends(get_session),
):
    logger.info(f'post_chat_message - Initiated')
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=403, detail="Login required")

    if model_id not in MODEL_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Invalid model id: {model_id}")

    # Create new conversation if needed
    if not conversation_id:
        form = await request.form()
        user_provided_name = form.get("conversation_name", "").strip()
        if user_provided_name:
            title = user_provided_name
        else:
        # Take first 30 chars of the user input as the title
            title = (user_input.strip()[:30] + "...") if len(user_input) > 30 else user_input.strip()
            if not title:
                # fallback to timestamp if empty
                title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        conv = create_conversation(session_db, user_id, name=title)
        print(f'New conversation created into user object storage==>\t{conv.messages}')
    else:
        conv = get_conversation(session_db, conversation_id, user_id)
        print(f'Retrived conversation from user object storage==>\t{conv.messages}')
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

    # Get AI response
    handler = get_model_handler(model_id)
    ai_response = handler(user_input) if handler else "Error: No valid model handler"
    
    append_message(session_db, conv.id, user_id, "user", user_input)
    append_message(session_db, conv.id, user_id, "assistant", ai_response)

    return {"user": user_input, "ai": ai_response, "conversation_id": conv.id}

# ---------- Save system prompt ----------
@router.post("/save_system_prompt")
async def save_system_prompt(
    request: Request,
    data: dict = Body(...),
    session_db: Session = Depends(get_session)
):
    logger.info(f'save_system_prompt - Initiated')
    user_id = request.session.get("user_id")
    conversation_id = data.get("conversation_id")
    prompt = data.get("prompt")
    logger.info(f'Passed data=>\nuser_id=> {user_id}\nconversation_id=> {conversation_id}\nprompt=> {prompt}')

    conv = get_conversation(session_db, conversation_id, user_id)
    logger.info(f'get_conversation - Accessed to retrive an existing conversation- {conversation_id} \nfrom user object storage: {session_db}')
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    update_conversation(session_db, conv, system_prompt=prompt)
    return {"status": "success", "saved_prompt": prompt}

# ---------- Export session ----------
@router.get("/export_session/{conversation_id}.{fmt}")
def export_session(
    request: Request,
    conversation_id: int,
    fmt: str,
    session_db: Session = Depends(get_session)
):
    logger.info(f'export_session - Initiated')
    user_id = request.session.get("user_id")
    conv = get_conversation(session_db, conversation_id, user_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if fmt == "md":
        logger.info(f'fmt == "md')
        content = "\n\n".join(
            f"**{m['role'].capitalize()}**: {m['content']}" for m in conv.messages
        )
        file_path = f"/tmp/chat_{conversation_id}.md"
        Path(file_path).write_text(content)
        return FileResponse(file_path, filename=f"conversation_{conversation_id}.md")

    elif fmt == "pdf":
        logger.info(f'fmt == "pdf')
        # Generate PDF here
        ...

    raise HTTPException(status_code=400, detail="Unsupported format")


# ---------- Delete conversation ----------
@router.post("/delete_session/{conversation_id}")
async def delete_conversation_route(
    request: Request,
    conversation_id: int,
    session_db: Session = Depends(get_session),
):
    logger.info(f'delete_conversation_route - Initiated for {conversation_id}')
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=403, detail="Login required")

    conv = get_conversation(session_db, conversation_id, user_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    session_db.delete(conv)
    session_db.commit()
    logger.info(f'Conversation {conversation_id} deleted for user {user_id}')

    # 👇 redirect to a new chat session with your default agent
    return RedirectResponse(url="/chat/model/mixtral", status_code=303)

