import json
from pprint import pprint
from typing import Self

import chromadb
from loguru import logger

from ragposium.api.datamodel import QueryResponse
from ragposium.lib.ingest import PaperMetadata


class CoreClient:
    """
    Singleton client for interacting with a ChromaDB instance.
    """

    singleton: Self | None = None

    def __init__(self) -> None:
        """
        Initialize the CoreClient and establish a connection to ChromaDB.
        """
        try:
            self.chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        except Exception as e:
            raise RuntimeError("Could not establish connection to Chroma.") from e

        if not any("ragposium" == col for col in self.chroma_client.list_collections()):
            self.chroma_client.create_collection(name="ragposium")

        self.collection = self.chroma_client.get_collection(name="ragposium")
        logger.success("Successfully connected to Chroma.")

    @classmethod
    def get_instance(cls) -> Self:
        """
        Get the singleton instance of the CoreClient.

        Returns:
            CoreClient: The singleton instance.
        """
        if cls.singleton is None:
            cls.singleton = cls()
        return cls.singleton

    def query_papers(self, query: str, n_results: int) -> QueryResponse:
        """
        Query the ChromaDB collection for matching papers.

        Args:
            query (str): The query string.
            n_results (int): The number of results to return.

        Returns:
            QueryResponse: A response containing matching papers.
        """
        results = self.collection.query(query_texts=query, n_results=n_results)
        metadatas: list[PaperMetadata] = []

        for metadata in (results.get("metadatas") or [])[0]:
            print(f"metadata: {json.dumps(metadata, indent=4)}")

            metadatas.append(
                PaperMetadata(
                    url=str(metadata["url"]),
                    title=str(metadata["title"]),
                    authors=str(metadata["authors"]),
                    abstract=str(metadata["abstract"]),
                )
            )

        pprint(metadatas)

        return QueryResponse(papers=metadatas, distances=[])
