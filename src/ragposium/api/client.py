import json
from pprint import pprint
from typing import Self, cast
from ragposium.lib.arxiv import ArxivPaper
from ragposium.lib.ingest import PaperMetadata
from ragposium.api.datamodel import QueryResponse
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
    
    def query_papers(self, query: str, n_results: int) -> QueryResponse:
        """Query matching papers."""

        results = self.collection.query(
            query_texts=query,
            n_results=n_results,
        )

        metadatas: list[PaperMetadata] = []


        for metadata in (results["metadatas"] or [])[0]:

            # metadata = cast(dict, metadata)

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
        print("type of metadatas:" ,type(metadatas[0]))

        return QueryResponse(
            papers=metadatas,
            distances=[]
        )

