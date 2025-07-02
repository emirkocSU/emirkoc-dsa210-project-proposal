# Multi-stage build for optimized production image
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

# Add metadata
LABEL maintainer="Premium Car Bot Team" \
      version="${VERSION}" \
      description="Premium Telegram Car Listing Alert Bot with YOLOv8 AI" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}"

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    cmake \
    pkg-config \
    libhdf5-dev \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libgtk2.0-dev \
    libcanberra-gtk-module \
    libxext6 \
    libsm6 \
    libxrender1 \
    libglib2.0-0 \
    libfontconfig1 \
    libice6 \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    libgtk-3-0 \
    libavcodec58 \
    libavformat58 \
    libswscale5 \
    libjpeg62-turbo \
    libpng16-16 \
    libtiff5 \
    libopenblas0 \
    liblapack3 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/models /app/temp && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . /app/

# Copy YOLOv8 model if available
COPY --chown=appuser:appuser models/ /app/models/

# Set permissions
RUN chmod +x /app/scripts/*.sh 2>/dev/null || true

# Create health check script
RUN echo '#!/bin/bash\n\
curl -f http://localhost:8080/health || exit 1' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh && \
    chown appuser:appuser /app/healthcheck.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /app/healthcheck.sh

# Default command
CMD ["python", "-m", "tgbot.main"]

# Alternative commands for different services
# Scheduler: CMD ["python", "-m", "tgbot.scheduler"]
# Worker: CMD ["python", "-m", "tgbot.worker"]