import typer
import uvicorn
from ragposium.lib.ingest import IngestionManager
from ragposium.api.endpoints import app as fastapi_app
from loguru import logger

app = typer.Typer()


@app.command(name="start", help="Start the ragposium server.")
def start():
    """Run the server."""
    logger.info("Starting server...")

    uvicorn.run(fastapi_app, host="0.0.0.0", port=8080)


@app.command(help="Run ingester")
def ingest():
    """Ingest data."""
    ingester = IngestionManager()
    ingester.ingest()


@app.command(help="Reset ragposium")
def reset():
    "Reset ragposium entries. This will require a re-ingestion."

    logger.warning(
        "Running this will require a reset of ragposium. Please enter `delete-ragposium` to continue."
    )

    if input("> ") != "delete-ragposium":
        logger.error("Aborting")
        return

    ingester = IngestionManager()
    ingester.chroma_client.delete_collection("ragposium")

    logger.info("Successfully deleted collection.")


if __name__ == "__main__":
    app()
