from typing import Any
from pydantic import BaseModel, Field


class EvaluationTestCase(BaseModel):
    test_id:str
    user_query: str
    customer_id: int 
    order_id: int | None = None
    expected_tool: str | list[str] | None = None
    expected_tool_args: dict[str, Any] = Field(default_factory=dict)
    ground_truth_facts: list[str] = Field(default_factory=list)


class AgentTrace(BaseModel):
    user_query: str
    retrieved_contexts: list[str] = Field(default_factory=list)
    tool_called: str | None = None
    tool_args: dict[str, Any] = Field(default_factory=dict)
    tool_output: str | None = None
    final_answer: str


class MetricGrade(BaseModel):
    reasoning: str = Field(
        description="Step-by-step chain of thought analyzing the agent's performance against this specific criterion."
    )
    score: int = Field(
        ge=1,
        le=5,
        description="Score from 1 (complete failure) to 5 (flawless).",
    )
    passed: bool = Field(
        description="True if score is 4 or 5, False otherwise."
    )


class JudgeVerdict(BaseModel):
    relevance: MetricGrade = Field(
        description="Does the final answer directly address the user's question without off-topic filler?"
    )
    correctness: MetricGrade = Field(
        description="Does the final answer match all expected ground_truth_facts from the test case?"
    )
    faithfulness: MetricGrade = Field(
        description="Is every claim in the final answer strictly supported by tool_output or retrieved_contexts with ZERO hallucinated dates, prices, or policies?"
    )
    helpfulness: MetricGrade = Field(
        description="Is the response clear, polite, well-structured, and actionable for a customer?"
    )