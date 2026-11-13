import asyncio
from itertools import islice
import logging
from typing import Iterable, TypeVar

from config import INDEX_NAME, NAMESPACE
from agents.graphs import embedding_model
from langchain_core.documents import Document
from langchain_pinecone.vectorstores import PineconeVectorStore
from scripts.ingest import ingestion

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
T = TypeVar("T")


def batched(iterable: Iterable[T], batch_size: int) -> Iterable[list[T]]:
    """Splits a list of documents into fixed-size batches (Pinecone recommends <= 100 per upsert)."""
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch


async def upload_to_pinecone(batch_size: int = 100) -> None:
    logger.info("Starting document loading and Markdown chunking...")
    chunks: list[Document] = ingestion()

    if not chunks:
        logger.warning("No Markdown chunks found in ./knowledge. Aborting upload.")
        return

    logger.info(
        "Prepared %d chunks. Connecting to Pinecone index '%s'...",
        len(chunks),
        INDEX_NAME,
    )

    store = PineconeVectorStore(
        index_name=INDEX_NAME,
        embedding=embedding_model,
        namespace=NAMESPACE,
    )
    total_uploaded = 0
    for batch_num, chunk_batch in enumerate(batched(chunks, batch_size), start=1):
        batch_ids = [chunk.metadata["id"] for chunk in chunk_batch]
        await store.aadd_documents(documents=chunk_batch, ids=batch_ids)

        total_uploaded += len(chunk_batch)
        logger.info(
            "Batch %d complete (%d/%d chunks upserted)",
            batch_num,
            total_uploaded,
            len(chunks),
        )


if __name__ == "__main__":
    asyncio.run(upload_to_pinecone(batch_size=100))