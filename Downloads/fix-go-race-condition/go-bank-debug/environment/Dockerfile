FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    golang-go \
    tmux \
    asciinema \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install uv (the required test runner)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Bake pytest into the uv environment so test.sh needs no network at runtime
RUN uv tool install pytest

WORKDIR /app

COPY server.go /app/server.go

RUN go build -o /app/server /app/server.go

CMD ["/app/server"]
