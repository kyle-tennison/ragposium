# Ragposium

[![Deployment](https://github.com/kyle-tennison/ragposium/actions/workflows/deploy.yml/badge.svg)](https://github.com/kyle-tennison/ragposium/actions/workflows/deploy.yml)
![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![FastAPI Logo](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)

Backend for [Ragposium](https://ragposium.com).

## Overview

Ragposium is a service for **retrieving academic papers using RAG**. For those who are not familiar, RAG stands for **Retrieval-Augmented Generation**; this process uses embedding matrices from large language models to create context-rich vectors of some text document—in this case, the academic paper. RAG is typically used within LLM workflows, but I think it can also be advantageous in research searches. Such an approach allows relevant papers to appear in a query, _even if the keywords/terminology are different._

Ragposium uses a **dataset of over 2 million papers** provided via Cornell University's [Arxiv](https://arxiv.org) service. This dataset is provided for free on behalf of [Kaggle](http://kaggle.com/).[^1] The _abstracts of these papers_ are ingested into [ChromaDB](https://www.trychroma.com/), a popular vector database. To reduce computing costs, Ragposium uses the default `all-MiniLM-L6-v2` embedding model provided with ChromaDB.

The ChromaDB stores the Arxiv dataset, along with a dataset of **10,000 common English words** provided by MIT's Eric Price [here](https://www.mit.edu/~ecprice/wordlist.10000). These words are ingested using the same `all-MiniLM-L6-v2` model and allow users to see what words have strong correlations with their query.

[^1]: The dataset can be found here: https://www.kaggle.com/datasets/Cornell-University/arxiv

## Contributing

For information on contributing, view [CONTRIBUTING.md](CONTRIBUTING.md)
