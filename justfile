self-sign:
    mkdir certs &
    mkcert -install
    mkcert -cert-file certs/localhost.pem -key-file certs/localhost-key.pem localhost 127.0.0.1 0.0.0.0 ::1

