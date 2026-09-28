# Multi-stage Dockerfile for Varsha (Non-root, Offline-First)

# --- Stage 1: Build Frontend Assets ---
FROM node:20-slim AS frontend-builder
WORKDIR /app/web
COPY web/package*.json ./
RUN npm install
COPY web/ ./
RUN npm run build

# --- Stage 2: Python Runtime ---
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python package
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy application code and configs
COPY src/ ./src/
COPY configs/ ./configs/
COPY scripts/ ./scripts/
COPY docs/ ./docs/
COPY --from=frontend-builder /app/web/dist ./web/dist

# Create non-root user
RUN useradd -m -u 1000 varshauser && \
    mkdir -p /app/products /app/data && \
    chown -R varshauser:varshauser /app

USER varshauser

EXPOSE 8000
ENV DATA_MODE=synthetic
ENV PORT=8000
ENV HOST=0.0.0.0

CMD ["python", "-m", "varsha.cli", "serve", "--port", "8000", "--host", "0.0.0.0"]
