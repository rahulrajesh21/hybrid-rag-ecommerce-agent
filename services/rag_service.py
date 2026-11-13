from langchain_pinecone.vectorstores import PineconeVectorStore
from langchain_core.documents import Document
from fastapi import Depends
from agents.graphs import embedding_model
from config import INDEX_NAME,NAMESPACE
from models.search_result_item import SearchResultItem
from langchain_community.retrievers.bm25 import BM25Retriever
from scripts.ingest import ingestion
import asyncio

def get_vector_store()->PineconeVectorStore:
    return PineconeVectorStore(
    index_name=INDEX_NAME,
    embedding=embedding_model,
    namespace=NAMESPACE
    )

def get_bm25_retriever(k: int = 4) -> BM25Retriever:
    chunks = ingestion()
    return BM25Retriever.from_documents(documents=chunks, k=k*3)


def reciprocal_rank_fusion(docs_pair:list[list[Document]])->list[Document]:

    document_score = {}
    document_mapping = {}
    for docs in docs_pair:
        for rank,doc in enumerate(docs,start=1):
            if doc.page_content not in document_score:
                document_score[doc.page_content] = 1/(60+rank)
                document_mapping[doc.page_content] = doc
                continue

            document_score[doc.page_content] += 1/(60+rank)

    sorted_docs = sorted(document_score,key=lambda x:document_score[x],reverse=True)

    return [document_mapping[id] for id in sorted_docs]
            



async def get_top_k(store:PineconeVectorStore,BM25Retrieve:BM25Retriever,topK:int,query:str)-> list[SearchResultItem]:
    if not query or not query.strip():
        return []
        
    scored_documents, bm25_document = await asyncio.gather(
         store.asimilarity_search(query=query,k=topK*3,score_threshold = 0.75),
         BM25Retrieve.ainvoke(input=query)
         )

    if not scored_documents:
        return []


    rrf_document = reciprocal_rank_fusion([scored_documents,bm25_document])

    document_list = [SearchResultItem(content=doc.page_content,metadata=doc.metadata) for doc in rrf_document[:topK]]
    return document_list
