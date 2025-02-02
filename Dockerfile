
# Use the official Python image from DockerHub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y     ffmpeg     libsndfile1     && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and poetry.lock (if exists) into the container
COPY pyproject.toml poetry.lock* /app/

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# Copy the application code
COPY . /app

# Expose the port for the hosted service (default for Typer-based APIs)
EXPOSE 8000

# Default command for running the CLI tool
CMD ["python", "-m", "audiokit.cli"]
