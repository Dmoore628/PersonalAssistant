FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache  
COPY libs/archi_core ./libs/archi_core
COPY services/hud_overlay/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -e ./libs/archi_core && \
    pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/hud_overlay ./hud_overlay

# Set environment variables
ENV PYTHONPATH=/app
ENV SERVICE_NAME=hud-overlay

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the service
CMD ["python", "-m", "uvicorn", "hud_overlay.main:app", "--host", "0.0.0.0", "--port", "8000"]