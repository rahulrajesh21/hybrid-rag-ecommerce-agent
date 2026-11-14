from models.chat_request import ChatRequest
from langchain_pinecone.vectorstores import PineconeVectorStore
from services.rag_service import get_top_k
from langchain_community.retrievers.bm25 import BM25Retriever
from langchain.messages import HumanMessage,SystemMessage
from models.ai_response import AIResponse
from agents.graphs import model,config
from agents.system_prompt import SYSTEM_PROMPT




async def chat_service(payload:ChatRequest,store:PineconeVectorStore,bm25_retriever:BM25Retriever) -> AIResponse:

    scored_documents = await get_top_k(store=store,BM25Retrieve=bm25_retriever,topK=4,query=payload.message)

    context_text = "\n\n---\n\n".join(
        f"Source({doc.metadata.get('filename','unknown')}):\n{doc.content}"
        for doc in scored_documents
    ) or "No relevant product documents found."

    messages = [
        SystemMessage(content=f"{SYSTEM_PROMPT}\n\n Context:\n{context_text}"),
        HumanMessage(
            content=payload.message
        )
    ]
    run_config = {
        "configurable": {
            "thread_id": payload.session_id,
            "customer_id":payload.customer_id
        }
    }
    response = await model.ainvoke({
        "messages":messages
    },config=run_config)

    raw_content = response["messages"][-1].content
    if isinstance(raw_content, list):
        text_parts = []
        for part in raw_content:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            elif isinstance(part, str):
                text_parts.append(part)
            elif hasattr(part, "text"):
                text_parts.append(part.text)
        ai_reply = "".join(text_parts)
    elif isinstance(raw_content, str):
        ai_reply = raw_content
    else:
        ai_reply = str(raw_content)
    return AIResponse(answer=ai_reply, session_id=payload.session_id, sources=scored_documents)