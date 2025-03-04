import typer
import uvicorn
from ragposium.cli.ingest import IngestionManager
from ragposium.api.commands import app

app = typer.Typer()

@app.command()
def server():
    """Run the server."""
    print("Starting server...")

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)



@app.command()
def ingest():
    """Ingest data."""
    ingester = IngestionManager()
    ingester.ingest()


if __name__ == "__main__":
    app()
