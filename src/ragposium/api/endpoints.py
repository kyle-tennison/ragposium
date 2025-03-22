import re
from fastapi import FastAPI, HTTPException
import httpx
from ragposium.api.datamodel import QueryRequest, MessageResponse, PaperQueryResponse, DictionaryQueryResponse
from ragposium.api.client import CoreClient
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

app = FastAPI(
    title="Ragposium", description="API documentation for Ragposium", version="1.0.0", root_path="/api"
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

@app.post("/generate-citation")
async def get_arxiv_bibtex(arxiv_id: str) -> str:
    bib_url = f"https://arxiv.org/bibtex/{arxiv_id}"
    logger.info(f"Fetching bibtex citation at {bib_url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(bib_url)
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch BibTeX ({e.response.status_code}): {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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