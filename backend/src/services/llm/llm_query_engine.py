import json
from anthropic import Anthropic

from config.settings import settings
from services.llm.sql_runner import SqlRunner, SqlValidationError
from services.llm.system_prompt import SYSTEM_PROMPT
from services.llm.tools import RUN_SQL_QUERY_TOOL
from config.logger import get_logger
from services.llm.llm_dataclass import LLMConfig, LLMQueryEngineResult

logger = get_logger(__name__)

class LLMQueryEngine:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.sql_runner = SqlRunner()
        self.llm_config = LLMConfig()

    def ask(self, question: str) -> LLMQueryEngineResult:
        messages = [{"role": "user", "content": question}]
        executed_queries: list[str] = []
        logger.info(f"LLMQueryEngine received question: {question}")
        for _ in range(self.llm_config.max_turns):
            # Initial call is a tool_use request, which may include SQL queries to run
            # Second call is a text response, which may include the final answer
            # act -> observe -> act -> observe -> ... until the LLM produces a final answer or max_turns is reached
            response = self.client.messages.create(
                model=self.llm_config.model,
                max_tokens=self.llm_config.max_tokens,
                system=self.llm_config.system_prompt,
                tools=self.llm_config.tools,
                messages=messages,
            )
            logger.info(f"LLM response: {response}")

            if response.stop_reason == "refusal":
                return LLMQueryEngineResult(answer="I'm not able to answer that question.", sql_queries=executed_queries)

            if response.stop_reason != "tool_use":
                return LLMQueryEngineResult(answer=self._extract_text(response), sql_queries=executed_queries)

            # Appends initial user question and LLM response to messages
            messages.append({"role": "assistant", "content": response.content})
            # Run any tools (e.g., SQL queries) that the LLM requested, and append the results to messages
            logger.info(f"Running tools: {response.content}")
            messages.append({"role": "user", "content": self._run_tools(response, executed_queries)})
        
        raise RuntimeError(f"QueryEngine did not produce a final answer within {self.llm_config.max_turns} turns")

    def _run_tools(self, response, executed_queries: list[str]) -> list[dict]:
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            query = block.input.get("query", "")
            try:
                rows = self.sql_runner.run(query)
                executed_queries.append(query)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(rows, default=str),
                })
            except SqlValidationError as e:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(e),
                    "is_error": True,
                })
            except Exception as e:
                logger.exception("Error running LLM-generated SQL query")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": f"Query failed: {e}",
                    "is_error": True,
                })
        return tool_results


    def _extract_text(self, response) -> str:
        return "".join(block.text for block in response.content if block.type == "text")
