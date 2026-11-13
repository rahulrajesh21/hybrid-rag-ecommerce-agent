from pydantic import BaseModel
from models.search_result_item import SearchResultItem


class AIResponse(BaseModel):
    answer:str
    session_id:str
    sources:list[SearchResultItem]