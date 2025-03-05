from ragposium.lib.arxiv import ArxivPaper
from ragposium.lib.ingest import PaperMetadata
from pydantic import BaseModel

class MessageResponse(BaseModel):
    """Generic request for messages."""
    message: str


class QueryRequest(BaseModel):
    """Requests papers corresponding to a query."""
    query: str 
    n_results: int


class QueryResponse(BaseModel):
    """Response to paper query."""
    papers: list[PaperMetadata]
    distances: list[float]
