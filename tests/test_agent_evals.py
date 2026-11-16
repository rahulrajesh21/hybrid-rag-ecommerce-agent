import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from langchain.messages import AIMessage, ToolMessage, HumanMessage
from models.chat_request import ChatRequest
from services.chat_service import chat_service
from agents.graphs import model
from tests.eval_judge import model as judge
from tests.eval_schemas import EvaluationTestCase, JudgeVerdict, AgentTrace
from services.rag_service import get_vector_store, get_bm25_retriever

DATASET_PATH = Path(__file__).parent / "golden_dataset.json"


def load_dataset_cases() -> list[EvaluationTestCase]:
    raw_data = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    return [EvaluationTestCase(**item) for item in raw_data]


def build_agent_trace(user_query: str, messages: list, final_answer: str, sources: list) -> AgentTrace:
    tool_called = None
    tool_args = {}
    tool_output = None

    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            first_call = msg.tool_calls[0]
            tool_called = first_call.get("name")
            tool_args = first_call.get("args", {})
        elif isinstance(msg, ToolMessage):
            tool_output = str(msg.content)

    return AgentTrace(
        user_query=user_query,
        retrieved_contexts=[doc.content for doc in sources],
        tool_called=tool_called,
        tool_args=tool_args,
        tool_output=tool_output,
        final_answer=final_answer,
    )


async def grade_agent_trace(case: EvaluationTestCase, trace: AgentTrace) -> JudgeVerdict:
    result = await judge.ainvoke({
        "messages": [
            HumanMessage(content=f"""
=== TEST CASE ===
{case.model_dump_json(indent=2)}

=== ACTUAL AGENT TRACE ===
{trace.model_dump_json(indent=2)}
""")
        ]
    })
    return result["structured_response"]


async def run_evaluations(store, bm25_retriever):
    test_cases = load_dataset_cases()
    passed_count = 0

    print(f"\n=======================================================")
    print(f"RUNNING NOVA-GEAR EVALUATION SUITE ({len(test_cases)} CASES)")
    print(f"=======================================================\n")

    for idx, case in enumerate(test_cases, start=1):
        session_id = f"eval_session_{case.test_id}"
        payload = ChatRequest(
            message=case.user_query,
            customer_id=case.customer_id,
            session_id=session_id
        )

        ai_response = await chat_service(
            payload=payload,
            store=store,
            bm25_retriever=bm25_retriever,
        )

        snapshot = await model.aget_state(config={"configurable": {"thread_id": session_id}})
        saved_messages = snapshot.values.get("messages", [])

        trace = build_agent_trace(
            user_query=case.user_query,
            messages=saved_messages,
            final_answer=ai_response.answer,
            sources=ai_response.sources
        )

        verdict = await grade_agent_trace(case=case, trace=trace)

    
        if isinstance(case.expected_tool, list):
            tool_ok = trace.tool_called in case.expected_tool
        else:
            tool_ok = (trace.tool_called == case.expected_tool)
        all_passed = bool(
            tool_ok
            and verdict.relevance.passed
            and verdict.correctness.passed
            and verdict.faithfulness.passed
            and verdict.helpfulness.passed
        )

        status = " PASS" if all_passed else " FAIL"
        if all_passed:
            passed_count += 1

        print(f"[{idx}/{len(test_cases)}] {status} [{case.test_id}] - {case.user_query}")
        print(f"    • Tool Invoked: {trace.tool_called} (Expected: {case.expected_tool}) -> {'OK' if tool_ok else 'MISMATCH'}")
        print(f"    • Relevance:    {verdict.relevance.score}/5 ({verdict.relevance.reasoning[:60]}...)")
        print(f"    • Correctness:  {verdict.correctness.score}/5 ({verdict.correctness.reasoning[:60]}...)")
        print(f"    • Faithfulness: {verdict.faithfulness.score}/5 ({verdict.faithfulness.reasoning[:60]}...)")
        print(f"    • Helpfulness:  {verdict.helpfulness.score}/5 ({verdict.helpfulness.reasoning[:60]}...)\n")

    pass_rate = (passed_count / len(test_cases)) * 100
    print(f"=======================================================")
    print(f" SUMMARY: {passed_count}/{len(test_cases)} Passed ({pass_rate:.1f}%)")
    print(f"=======================================================\n")


if __name__ == "__main__":
    store = get_vector_store()
    bm25 = get_bm25_retriever()
    asyncio.run(run_evaluations(store, bm25))
