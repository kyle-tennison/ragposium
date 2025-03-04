import typer
from ragposium.app.ingest import IngestionManager

app = typer.Typer()

@app.command()
def server():
    """Run the server."""
    print("Starting server...")

@app.command()
def ingest():
    """Ingest data."""
    ingester = IngestionManager()

    ingester.run()




if __name__ == "__main__":
    app()
