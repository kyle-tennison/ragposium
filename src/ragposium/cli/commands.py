from pathlib import Path
import typer
import uvicorn
from ragposium.lib.ingest import IngestionManager
from ragposium.api.endpoints import app as fastapi_app
from loguru import logger
from ragposium.api.client import CoreClient

app = typer.Typer(pretty_exceptions_enable=False)


@app.command(name="start", help="Start the ragposium server.")
def start():
    """Run the server."""
    logger.info("Starting server...")

    CoreClient.get_instance()  # connect to chroma

    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=8080,
    )


@app.command(help="Run ingester")
def ingest():
    """Ingest data."""
    ingester = IngestionManager()
    ingester.ingest()


@app.command(help="Reset ragposium")
def reset():
    "Reset ragposium entries. This will require a re-ingestion."

    logger.warning(
        "Running this will permanently delete the targeted collections. Backup before running."
    )

    logger.info("Info the name of the collection to delete.")

    target_collection = input("> ")

    ingester = IngestionManager()
    ingester.chroma_client.delete_collection(target_collection)

    logger.info("Successfully deleted collection.")


if __name__ == "__main__":
    app()
