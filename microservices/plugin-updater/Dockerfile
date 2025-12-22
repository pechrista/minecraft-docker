# Start with the recommended lightweight image
FROM python:3.12-slim

# 1. Install Docker CLI & Compose via official convenience script
# This handles GPG keys, repositories, and plugins automatically.
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh && \
    rm -rf /var/lib/apt/lists/*

# 2. Install Python dependencies
RUN pip install --no-cache-dir requests PyYAML docker

WORKDIR /app
COPY src/ /app/src/
ENV PYTHONPATH=/app
