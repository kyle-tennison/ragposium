self-sign:
    mkdir certs &
    mkcert -install
    mkcert -cert-file certs/localhost.pem -key-file certs/localhost-key.pem localhost 127.0.0.1 0.0.0.0 ::1

restart:
    docker compose down
    docker compose build
    docker compose up