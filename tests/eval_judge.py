import os
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from tests.eval_schemas import JudgeVerdict
from langchain_openai import ChatOpenAI

OMLX_BASE_URL = os.getenv("OMLX_BASE_URL", "http://127.0.0.1:8000/v1")
OMLX_API_KEY = os.getenv("OMLX_API_KEY", "oMLX")
OMLX_MODEL = os.getenv("OMLX_MODEL", "Qwen3-14B-MLX-6bit")

local_llm = ChatOpenAI(
    base_url=OMLX_BASE_URL,
    api_key=OMLX_API_KEY,
    model=OMLX_MODEL,
    temperature=0.0,
    max_tokens=2048,
)

JUDGE_SYSTEM_PROMPT = """
You are a strict QA evaluator for NovaGear customer support.
Grade the agent's Final Answer strictly against Ground Truth Facts, Tool Output, and Retrieved Contexts.
- Any invented date, price, order status, or policy not found in the provided Tool Output or Retrieved Contexts MUST score 1 or 2 on faithfulness. (Information present in Retrieved Contexts or Tool Output is faithful).
- A response missing required Ground Truth Facts MUST score 3 or lower on correctness.
- Write concise reasoning citing exact evidence before setting score and passed (passed = score >= 4).
"""

model = create_agent(
    model=local_llm,
    tools=[],
    system_prompt=JUDGE_SYSTEM_PROMPT,
    response_format=JudgeVerdict
)
