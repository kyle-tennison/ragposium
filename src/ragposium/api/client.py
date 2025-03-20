import json
from pprint import pprint
from typing import Self

import chromadb
from loguru import logger

from ragposium.api.datamodel import PaperQueryResponse
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
            self.chroma_client = chromadb.HttpClient(host="chroma", port=8000)
        except Exception as e:
            raise RuntimeError("Could not establish connection to Chroma.") from e

        self.paper_collection = self.chroma_client.get_collection(name="ragposium")
        self.dictionary_collection = self.chroma_client.get_collection(name="dictionary")
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

    def query_papers(self, query: str, n_results: int) -> PaperQueryResponse:
        """
        Query the ChromaDB collection for matching papers.

        Args:
            query: The query string.
            n_results: The number of results to return.

        Returns:
            A response containing matching papers.
        """

        logger.info(f"Querying Chroma for {n_results} papers...")
        results = self.paper_collection.query(query_texts=query, n_results=n_results)
        logger.success(f"Chroma responded to paper query")
        logger.debug(f"Query response was: {results}")

        metadatas: list[PaperMetadata] = []
        distances: list[float] = (results.get("distances") or [])[0]

        for metadata in (results.get("metadatas") or [])[0]:
            metadatas.append(
                PaperMetadata(
                    url=str(metadata["url"]),
                    title=str(metadata["title"]),
                    authors=str(metadata["authors"]),
                    abstract=str(metadata["abstract"]),
                )
            )

        return PaperQueryResponse(papers=metadatas, distances=distances)


    def query_dictionary(self, query: str, n_results: int) -> tuple[list[str], list[float]]:
        """
        Query the ChromaDB dictionary collection to get the top n words that
        correspond to a query.

        Args:
            query: The query string
            n_results: The number of results to return

        Returns:
            A list of aligned words and a list of the corresponding distances
        """

        logger.info(f"Querying Chroma for {n_results} dictionary words...")
        results = self.dictionary_collection.query(query_texts=query, n_results=n_results)
        logger.success(f"Chroma responded to dictionary query")
        logger.debug(f"Query response was: {results}")

        words: list[str] = results.get("ids")[0]
        distances: list[float] = (results.get("distances") or [])[0]

        return words, distances