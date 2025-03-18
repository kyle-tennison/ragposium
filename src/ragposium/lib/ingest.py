from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from typing import Iterator

import chromadb
import kagglehub
from loguru import logger
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from torch import Tensor
from tqdm import tqdm

from ragposium.lib.arxiv import ArxivPaper


class PaperMetadata(BaseModel):
    """
    Metadata representation of an arXiv paper.

    Attributes
    ----------
    url : str
        The URL of the paper.
    title : str
        The title of the paper.
    authors : str
        The authors of the paper.
    abstract : str
        The abstract of the paper.
    """

    url: str
    title: str
    authors: str
    abstract: str


class IngestionManager:
    """
    Manages the ingestion of arXiv data into a ChromaDB collection.
    """

    def __init__(self) -> None:
        """
        Initializes the ingestion manager and establishes a connection to ChromaDB.

        Raises
        ------
        RuntimeError
            If the connection to ChromaDB cannot be established.
        """
        logger.debug("Connecting to Chroma...")
        try:
            self.chroma_client = chromadb.HttpClient(host="chroma", port=8000)
        except Exception as e:
            raise RuntimeError("Could not establish connection to Chroma.") from e

        if not any("ragposium" == col for col in self.chroma_client.list_collections()):
            self.chroma_client.create_collection(name="ragposium")

        self.collection = self.chroma_client.get_collection(name="ragposium")
        logger.success("Successfully connected to Chroma.")

        self.dataset_dir = self.download_datasets()
        self.arxiv_dataset = self.dataset_dir / "arxiv-metadata-oai-snapshot.json"

    def download_datasets(self) -> Path:
        """
        Downloads the necessary datasets using Kaggle.

        Returns
        -------
        Path
            The directory containing the downloaded dataset.
        """
        return Path(kagglehub.dataset_download("Cornell-University/arxiv"))

    def count_datasets(self) -> int:
        """
        Counts the number of entries in the arXiv dataset.

        Returns
        -------
        int
            The number of dataset entries.
        """
        logger.info("Counting entries...")
        with self.arxiv_dataset.open("r") as f:
            count = sum(1 for _ in f.readlines())
        logger.info(f"Counted {count} entries")
        return count

    def iter_arxiv(self) -> Iterator[ArxivPaper]:
        """
        Iterates over the arXiv papers available in the dataset.

        Yields
        ------
        ArxivPaper
            An instance representing an arXiv paper.
        """
        MAX_ITER = 100000
        with self.arxiv_dataset.open("r") as f:
            for i, line in enumerate(f.readlines()):
                if i > MAX_ITER:
                    return
                yield ArxivPaper(**json.loads(line))

    def embed_abstract(self, abstract: str) -> Tensor:
        """
        Generates an embedding for a paper's abstract.

        Parameters
        ----------
        abstract : str
            The abstract text of the paper.

        Returns
        -------
        Tensor
            The embedding vector representation.
        """
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(abstract)

    def ingest(self) -> None:
        """
        Ingests papers into the ChromaDB collection, ensuring no duplicates.
        """
        already_included = 0
        total_entries = self.count_datasets()

        for paper in tqdm(self.iter_arxiv(), total=total_entries, desc="Ingesting"):
            if self.collection.get(paper.id)["ids"]:
                already_included += 1
                continue

            if paper.abstract and paper.id:
                if "this paper has been withdrawn" in paper.abstract.lower():
                    continue

                metadata = PaperMetadata(
                    url=f"https://arxiv.org/abs/{paper.id}",
                    title=paper.title or "Untitled",
                    authors=paper.authors or "",
                    abstract=paper.abstract,
                )

                self.collection.add(
                    ids=paper.id,
                    documents=paper.abstract,
                    metadatas=metadata.model_dump(mode="json"),
                )
