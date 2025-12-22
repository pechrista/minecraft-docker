# Start with the recommended lightweight image
FROM python:3.12-slim

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    # Clean up APT cache to keep the image size down
    && rm -rf /var/lib/apt/lists/*

# Install Docker Compose as a plugin
# This is the standard, modern way to install Compose on Linux
RUN mkdir -p /usr/local/lib/docker/cli-plugins && \
    curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose && \
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Install Python dependencies
RUN pip install --no-cache-dir \
    requests \
    PyYAML \
    docker

# Set working directory
WORKDIR /app

# Copy the plugin updater source
COPY src/ /app/src/
COPY plugin-updater.cfg /app/

# Set PYTHONPATH to include src directory
ENV PYTHONPATH=/app

# Run the main script
CMD ["python", "-u", "src/main.py", "--config", "plugin-updater.cfg"]