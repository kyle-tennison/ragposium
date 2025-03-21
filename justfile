self-sign:
    mkdir certs &
    mkcert -install
    mkcert -cert-file certs/localhost.pem -key-file certs/localhost-key.pem localhost 127.0.0.1 0.0.0.0 ::1

restart-dev:
    docker compose -f docker/docker-compose-dev.yml down
    docker compose -f docker/docker-compose-dev.yml build
    docker compose -f docker/docker-compose-dev.yml up

# docker-push:
#     docker build -t kyletennison/ragposium-api:latest -f docker/Dockerfile.api .
#     docker build -t kyletennison/ragposium-frontend:latest -f docker/Dockerfile.frontend .
#     docker push kyletennison/ragposium-api:latest 
#     docker push kyletennison/ragposium-frontend:latest 

restart-prod:
    docker compose -f docker/docker-compose-prod.yml down
    docker compose -f docker/docker-compose-prod.yml build
    docker compose -f docker/docker-compose-prod.yml up

certbot:
    