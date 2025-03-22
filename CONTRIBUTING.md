# Contributing

## Local Setup

### Submodule

The [react site](https://github.com/kyletennison/ragposium-react) is provided as a submodule to this repository. After cloning, you may need to run the following to load the submodule:

```bash
git submodule update --init --recursive
```

### Docker Compose

To spin up the containers locally, install [Docker](https://www.docker.com/) and run:

```bash
docker compose -f docker/docker-compose-dev.yml up
```

Alternatively, the cluster can be refreshed (down, build, up) using:

```bash
just restart-dev
```

from the repo root to start the server and [ChromaDB](https://www.trychroma.com/) instances.

## Deployment

### SSL Certificates

Install certbot:

```bash
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Then, generate the certificates with

```bash
sudo certbot certonly -d ragposium.com -d www.ragposium.com
```

When prompted on the method of authentication, it is usually easiest to momentarily host a webserver such that certbot can automatically preform the ACME challenge; this is (as of March 2025) the first option (1) that certbot provides. After runnind this command, the [production docker compose file](docker/docker-compose-prod.yml) will automatically be able to reference the certificates.

### Deployment

To refresh the deployment, run `sudo just restart-prod`.

