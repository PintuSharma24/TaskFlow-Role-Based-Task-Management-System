
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.database.connection import get_db
from app.models.user import User
from app.api.v1.chatbot.chatbot import process_manager_question


# Router definition
router = APIRouter(
    prefix="/chatbot",
    tags=["TaskFlow AI Chatbot"]
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatSource(BaseModel):
    source_type: str
    source_id: int


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]


@router.post("/ask", response_model=ChatResponse)
async def ask_chatbot(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager"))
):
    try:
        result = await process_manager_question(
    db=db,
    manager_id=current_user.id,
    question=request.message)

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except Exception as error:
        print(f"Chatbot error: {error}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question."
        )
