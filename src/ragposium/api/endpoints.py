from fastapi import FastAPI, HTTPException
from ragposium.api.datamodel import QueryRequest, MessageResponse, QueryResponse
from ragposium.api.client import CoreClient
from fastapi.middleware.cors import CORSMiddleware

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


@app.post("/query")
def query_endpoint(request: QueryRequest) -> QueryResponse:
    """Query the database for matching papers."""

    if request.n_results > 20:
        raise HTTPException(
            status_code=400, detail="Only 20 results can be listed at a time."
        )

    client = CoreClient.get_instance()
    papers = client.query_papers(
        query=request.query,
        n_results=request.n_results,
    )

    return papers
