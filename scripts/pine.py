import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

pc.create_index(
    name=os.getenv("INDEX_NAME", "novagear-support"),
    dimension=1024,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)