from ninja import Router, Schema
from typing import Optional
import asyncio
import logging

from services.llm.llm_query_engine import LLMQueryEngine

logger = logging.getLogger(__name__)

router = Router()


class AskRequest(Schema):
    question: str


class AskResponseSchema(Schema):
    success: bool
    answer: Optional[str] = None
    error: Optional[str] = None


@router.post("/ask", response=AskResponseSchema)
async def ask(request, payload: AskRequest):
    try:
        def sync_ask():
            return LLMQueryEngine().ask(payload.question).answer

        answer = await asyncio.to_thread(sync_ask)
        return AskResponseSchema(success=True, answer=answer)
    except Exception as e:
        logger.exception("Error answering LLM query")
        return AskResponseSchema(success=False, error=str(e))
