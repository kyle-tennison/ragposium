from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
from typing import Iterator
import uuid

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

        # create collections if they don't already exist
        if not any("ragposium" == col for col in self.chroma_client.list_collections()):
            self.chroma_client.create_collection(name="ragposium")
        if not any("dictionary" == col for col in self.chroma_client.list_collections()):
            self.chroma_client.create_collection(name="dictionary")

        # load collections
        self.paper_collection = self.chroma_client.get_collection(name="ragposium")
        self.dictionary_collection = self.chroma_client.get_collection(name="dictionary")
        logger.success("Successfully connected to Chroma.")

        self.dataset_dir = self.download_papers()
        self.arxiv_dataset = self.dataset_dir / "arxiv-metadata-oai-snapshot.json"

    def download_papers(self) -> Path:
        """
        Downloads a dataset of Arxiv papers through Kaggle.
        
        Returns
        -------
        Path
            The directory that contains the downloaded dataset.
        """

        logger.info("Downloading arxiv papers...")
        dataset_dir = Path("/kaggle-data/papers")

        if dataset_dir.exists():
            logger.info("Papers dataset already in volume")
            return dataset_dir
            
        output_dir = Path(kagglehub.dataset_download("Cornell-University/arxiv"))
        try:
            shutil.move(output_dir, dataset_dir)
        except OSError as e:
            logger.warning(f"Failed to move papers dataset to persistent dir. "
                           "This usually happens because ragposium is running "
                           f"outside of its container. The error is: {e}")
            return output_dir
        else:
            return dataset_dir
            
    
    def download_dictionary(self) -> Path:
        """
        Downloads a dataset of english words through Kaggle.
        
        Returns
        -------
        Path
            The directory that contains the downloaded dataset.
        """
        
        logger.info("Downloading words dataset...")
        dataset_dir = Path("/kaggle-data/dictionary")

        if dataset_dir.exists():
            logger.info("Words dataset already in volume")
            return dataset_dir

        output_dir = Path(kagglehub.dataset_download("rtatman/english-word-frequency"))
        try:
            shutil.move(output_dir, dataset_dir)
        except OSError as e:
            logger.warning(f"Failed to move dict dataset to persistent dir. "
                           "This usually happens because ragposium is running "
                           f"outside of its container. The error is: {e}")
            return output_dir
        else:
            return dataset_dir


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


    def ingest(self) -> None:
        self.ingest_words()
        self.ingest_papers()

    def ingest_words(self) -> None:
        """Ingest words into the dictionary database."""
        
        words = []

        dictionary_dataset = self.download_dictionary() / "unigram_freq.csv"
        with dictionary_dataset.open() as f:
            for i, line in enumerate(f.readlines()):

                # skip headers
                if i == 0:
                    continue

                if i < 150_000:
                    words.append(line.split(',')[1].strip())


        for word in tqdm(words, desc="Ingesting Dictionary"):
            if self.dictionary_collection.get(word)["ids"]:
                continue

            self.dictionary_collection.add(
                ids=word,
                documents=word
            )


    def ingest_papers(self) -> None:
        """
        Ingests papers into the ChromaDB collection, ensuring no duplicates.
        """
        already_included = 0
        total_entries = self.count_datasets()

        for paper in tqdm(self.iter_arxiv(), total=total_entries, desc="Ingesting Papers"):
            if self.paper_collection.get(paper.id)["ids"]:
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

                self.paper_collection.add(
                    ids=paper.id,
                    documents=paper.abstract,
                    metadatas=metadata.model_dump(mode="json"),
                )
