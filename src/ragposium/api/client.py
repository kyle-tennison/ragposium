from typing import Self
from ragposium.lib.arxiv import ArxivPaper
import chromadb
from loguru import logger



class CoreClient:
    singleton: Self | None = None

    def __init__(self) -> None:

        try:
            self.chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        except:
            raise RuntimeError(f"Could not establish connection to chroma.")

        if not any("ragposium" == col for col in self.chroma_client.list_collections()):
            self.chroma_client.create_collection(name="ragposium")

        self.collection = self.chroma_client.get_collection(name="ragposium")

        logger.success("Successfully connected to Chroma.")

    @classmethod
    def get_instance(cls) -> Self:
        """Get the singleton instance of the CoreClient"""
        if not cls.singleton:
            cls.singleton = cls()
        return cls.singleton
    
    def query_papers(self, query: str, n_results: int) -> list[ArxivPaper]:
        """Query matching papers."""

        results = self.collection.query(
            query_texts=query,
            n_results=n_results,
        )

        

        print(results)

        return []

