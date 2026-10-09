from ninja import Router, Schema
from typing import List, Optional
import asyncio
import logging
import time

from services.llm.llm_query_engine import LLMQueryEngine
from services.redis.redis_client import RedisClient
from ninja_jwt.authentication import AsyncJWTAuth


logger = logging.getLogger(__name__)

router = Router(auth=AsyncJWTAuth(), tags=["llm"])


class AskRequest(Schema):
    question: str


class AskResponseSchema(Schema):
    success: bool
    answer: Optional[str] = None
    answers: Optional[List[dict]] = None
    error: Optional[str] = None


@router.post("/ask", response=AskResponseSchema)
async def ask(request, payload: AskRequest):
    try:
        def sync_ask():
            return LLMQueryEngine().ask(payload.question)
        user_id = request.user.id
        # Wall clock, not the monotonic loop.time(): the transcript needs a real date.
        time_requested = time.time()
        cache_client = RedisClient()
        answer = await asyncio.to_thread(sync_ask)
        cache_key = f"llm_query:{user_id}:{payload.question}:{time_requested}"
        cache_client.set(cache_key, answer.answer)

        return AskResponseSchema(success=True, answer=answer.answer)
    except Exception as e:
        logger.exception("Error answering LLM query")
        return AskResponseSchema(success=False, error=str(e))

@router.get("/get_conversation", response=AskResponseSchema)
def get_conversations(request):
    try:
        cache_client = RedisClient()
        user_id = request.user.id
        pattern = f"llm_query:{user_id}:*"
        matching_keys = cache_client.keys(pattern)

        if not matching_keys:
            return AskResponseSchema(success=False, error="No conversation found for the given session.")

        answers = []
        for key in matching_keys:
            question = key.split(":")[2]
            time_requested = key.split(":")[3]
            answer = cache_client.get(key)
            qa_dict = {"question": question, "answer": answer, "time_requested": time_requested}
            answers.append(qa_dict)
        ordered_answers = sorted(answers, key=lambda x: float(x["time_requested"]))
        return AskResponseSchema(success=True, answers=ordered_answers)
    except Exception as e:
        logger.exception("Error retrieving LLM conversation")
        return AskResponseSchema(success=False, error=str(e))
