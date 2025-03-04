from fastapi import FastAPI
from ragposium.api.datamodel import QueryRequest, MessageResponse, QueryResponse
from ragposium.api.client import CoreClient

app = FastAPI(
    title="Ragposium", description="API documentation for Ragposium", version="1.0.0"
)


@app.get("/")
def index() -> MessageResponse:
    return MessageResponse(message="Welcome to ragposium-core")


@app.get("/health")
def health() -> MessageResponse:
    CoreClient.get_instance()
    return MessageResponse(message="Healthy")


@app.post("/query")
def query_endpoint(request: QueryRequest) -> QueryResponse:

    client = CoreClient.get_instance()
    papers = client.query_papers(
        query=request.query,
        n_results=request.n_results,
    )



    return QueryResponse(papers=papers)
