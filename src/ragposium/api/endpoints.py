import re
from fastapi import FastAPI, HTTPException
from ragposium.api.datamodel import QueryRequest, MessageResponse, PaperQueryResponse, DictionaryQueryResponse
from ragposium.api.client import CoreClient
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

app = FastAPI(
    title="Ragposium", description="API documentation for Ragposium", version="1.0.0"
)


# Allow all origins (useful for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def index() -> MessageResponse:
    """Root of the API"""
    return MessageResponse(message="Welcome to ragposium-core")


@app.get("/health")
def health() -> MessageResponse:
    """Endpoint to check health."""
    CoreClient.get_instance()
    return MessageResponse(message="Healthy")


@app.post("/query-papers")
def query_papers(request: QueryRequest) -> PaperQueryResponse:
    """Query the database for matching papers."""

    logger.info(f"Received inbound paper query: {request!s}")

    if request.n_results > 200:
        raise HTTPException(
            status_code=400, detail="Only 200 documents can be listed at a time."
        )

    client = CoreClient.get_instance()
    papers = client.query_papers(
        query=request.query,
        n_results=request.n_results,
    )

    return papers

@app.post("/query-dict")
def query_dict(request: QueryRequest) -> DictionaryQueryResponse:
    """Query the dictionary database for similar words."""

    logger.info(f"Received inbound dictionary query: {request!s}")

    if request.n_results > 20:
        raise HTTPException(
            status_code=400, detail="Only 20 documents can be listed at a time."
        )
    
    client = CoreClient.get_instance()
    words, distances = client.query_dictionary(
        query=request.query,
        n_results=request.n_results,
    )

    return DictionaryQueryResponse(
        words=words,
        distances=distances
    )