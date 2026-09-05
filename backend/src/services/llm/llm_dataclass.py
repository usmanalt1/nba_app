from services.llm.system_prompt import SYSTEM_PROMPT
from services.llm.tools import RUN_SQL_QUERY_TOOL
from dataclasses import dataclass, field

MODEL = "claude-sonnet-5"
MAX_TURNS = 4

@dataclass
class LLMConfig:
    model: str = MODEL
    max_turns: int = MAX_TURNS
    system_prompt: str = SYSTEM_PROMPT
    max_tokens: int = 4096
    tools: list[dict] = field(default_factory=lambda: [RUN_SQL_QUERY_TOOL])

@dataclass
class LLMQueryEngineResult:
    answer: str
    sql_queries: list[str] = field(default_factory=list)