from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()
from api.v1.chat import router
from api.v1.customer import router as customer_router
from contextlib import asynccontextmanager
from services.rag_service import get_bm25_retriever
from db.db import Base,engine
@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind=engine)
    app.state.bm25_retriever = get_bm25_retriever()
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(
 router=router,
 prefix='/api/v1'
)
app.include_router(
    router=customer_router,
    prefix='/api/v1'
)
app.add_middleware(
    CORSMiddleware,
    allow_headers=['*'],
    allow_methods=['*'],
    allow_origins=['*'],
)