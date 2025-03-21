# Ragposium 

Backend for [Ragposium](https://ragposium.com).

## Local Setup

### SSL Certificates (for Development)

Install [`justfile`](https://github.com/casey/just) to run sh scripts:

```bash
cargo install just
# more ways to install provided in link above
```

Install [`mkcert`](https://github.com/FiloSottile/mkcert) to run locally:

You can install this with brew.

```bash
brew install mkcert # for chrome
brew install nss # for firefox
# more ways to install provided in link above
```

Then, run `just self-sign` in the repo root to create locally signed SSL certificates.
This should populate the `certs/` directory with localhost certificates.

### Docker Compose

To spin up the containers locally, install [Docker](https://www.docker.com/) and run:

```bash
docker compose -f docker/docker-compose-dev.yml up
```

from the repo root to start the server and [ChromaDB](https://www.trychroma.com/) instances.

## Deployment

## SSL Certificates

Use certbot to generate a 