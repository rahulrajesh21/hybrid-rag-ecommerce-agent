from fastapi import APIRouter,Request,Depends
from models.chat_request import ChatRequest
from langchain_pinecone.vectorstores import PineconeVectorStore
from services.rag_service import get_vector_store
from services.chat_service import chat_service
from langchain_community.retrievers.bm25 import BM25Retriever

router = APIRouter()


def get_bm25_from_state(request: Request) -> BM25Retriever:
    return request.app.state.bm25_retriever

@router.post(path='/chat')
async def chat(payload:ChatRequest,bm25_retriever:BM25Retriever = Depends(get_bm25_from_state),store:PineconeVectorStore = Depends(get_vector_store)):
    return await chat_service(payload=payload,store = store,bm25_retriever=bm25_retriever)
     