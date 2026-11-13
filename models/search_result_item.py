from pydantic import BaseModel

class SearchResultItem(BaseModel):
    content:str
    metadata:dict