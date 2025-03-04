from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from typing import Iterator
import chromadb
from pydantic import BaseModel
from torch import Tensor
from tqdm import tqdm
from ragposium.lib.arxiv import ArxivPaper
from loguru import logger
import kagglehub
from sentence_transformers import SentenceTransformer


class PaperMetadata(BaseModel):
    url: str
    title: str 
    authors: str
    abstract: str



class IngestionManager:
    """Ingest arXiv data into a Milvus database."""

    def __init__(self):
        logger.debug("Connecting to Chroma...")

        # self.chroma_client = chromadb.Client()
        try:
            self.chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        except:
            raise RuntimeError("Could not establish connection to Chroma.")

        if not any("ragposium" == col for col in self.chroma_client.list_collections()):
            self.chroma_client.create_collection(name="ragposium")

        self.collection = self.chroma_client.get_collection(name="ragposium")

        logger.success("Successfully connected to Chroma.")

        self.dataset_dir = self.download_datasets()
        self.arxiv_dataset = self.dataset_dir / "arxiv-metadata-oai-snapshot.json"

    def download_datasets(self) -> Path:
        """Download the necessary datasets. Cashes using kaggle.

        Returns:
            A path to the dataset download dir.
        """

        # Download latest version
        return Path(kagglehub.dataset_download("Cornell-University/arxiv"))

    def count_datasets(self) -> int:
        """Count the number of datasets."""

        logger.info("Counting entries....")
        with self.arxiv_dataset.open("r") as f:
            i = sum(1 for _ in f.readlines())

        logger.info(f"Counted {i} entries")
        return i

    def iter_arxiv(self) -> Iterator[ArxivPaper]:
        """Iterate over the ArXiv papers available."""

        MAX_ITER = 100000

        with self.arxiv_dataset.open("r") as f:
            for i, line in enumerate(f.readlines()):
                if i > MAX_ITER:
                    return
                yield ArxivPaper(**json.loads(line))

    def embed_abstract(self, abstract: str) -> Tensor:
        """Run the abstract of a paper through an embedding matrix."""

        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(abstract)

    def ingest(self):
        """Ingest the data into the collection."""

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
                    abstract=paper.abstract
                )


                self.collection.add(
                    ids=paper.id,
                    documents=paper.abstract,
                    metadatas=metadata.model_dump(mode="json")
                )
