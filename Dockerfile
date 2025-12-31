# Install uv
FROM python:3.14-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Generate requirements.txt from pyproject.toml
COPY pyproject.toml /app/pyproject.toml
RUN uv pip compile /app/pyproject.toml --output-file /app/requirements.txt

FROM python:3.14-slim

WORKDIR /app

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY --chown=app:app src /app/src

# Run the application
ENTRYPOINT ["python", "/app/src/pdf2cbz"]
