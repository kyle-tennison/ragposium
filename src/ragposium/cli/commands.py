import typer
import uvicorn
from ragposium.lib.ingest import IngestionManager
from ragposium.api.commands import app as fastapi_app

app = typer.Typer()

@app.command(help="Start the ragposium server.")
def start():
    """Run the server."""
    print("Starting server...")

    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, reload=True)



@app.command(help="Run ingester")
def ingest():
    """Ingest data."""
    ingester = IngestionManager()
    ingester.ingest()


if __name__ == "__main__":
    app()
