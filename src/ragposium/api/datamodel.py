from ragposium.lib.arxiv import ArxivPaper
from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class QueryRequest(BaseModel):
    query: str 
    n_results: int


class QueryResponse(BaseModel):
    papers: list[ArxivPaper]
