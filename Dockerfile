# ==============================================================================
# Multimodal EHR CDSS - Backend Dockerfile (Phase 2 - Production Ready)
# ==============================================================================
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-deploy.txt requirements-ml.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-deploy.txt

# Optional full ML runtime so /api/v1/predict/multimodal and /predict/baseline can serve
# the fitted checkpoints (Phase 3). Default 0 keeps the lightweight image (503 on those routes).
ARG INSTALL_ML=0
RUN if [ "$INSTALL_ML" = "1" ]; then \
      pip install --no-cache-dir torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu && \
      pip install --no-cache-dir -r requirements-ml.txt ; \
    fi
ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1

# Copy application source code and configurations
COPY configs/ /app/configs/
COPY src/ /app/src/

# Expose FastAPI service port
EXPOSE 8000

# Healthcheck definition
HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch FastAPI with Uvicorn
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
