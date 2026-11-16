from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from agents.system_prompt import SYSTEM_PROMPT
from agents.tools.order_tool import get_order_status,check_return_eligibility,delivery_estimate
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings

checkpoint = InMemorySaver()


embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    output_dimensionality = 1024
)

config = {
    "configurable":{
        "thread_id":"default"
    }
}


model = create_agent(
    model="google_genai:gemini-3.5-flash-lite",
    tools=[get_order_status,check_return_eligibility,delivery_estimate],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpoint,
)