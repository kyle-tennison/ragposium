restart-dev:
    docker compose -f docker/docker-compose-dev.yml down
    docker compose -f docker/docker-compose-dev.yml build
    docker compose -f docker/docker-compose-dev.yml up -d 

restart-prod:
    docker compose -f docker/docker-compose-prod.yml down
    docker compose -f docker/docker-compose-prod.yml build
    docker compose -f docker/docker-compose-prod.yml up -d
    
prod-watch:
    docker compose -f docker/docker-compose-prod.yml logs -f

dev-watch:
    docker compose -f docker/docker-compose-dev.yml logs -f