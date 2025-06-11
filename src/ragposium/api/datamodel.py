from ragposium.lib.ingest import PaperMetadata
from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Generic request for messages."""

    message: str


class QueryRequest(BaseModel):
    """Requests papers corresponding to a query."""

    query: str
    n_results: int


class PaperQueryResponse(BaseModel):
    """Response to paper query."""

    papers: list[PaperMetadata]
    distances: list[float]


class DictionaryQueryResponse(BaseModel):
    """Response to dictionary query."""

    words: list[str]
    distances: list[float]
