FROM oven/bun:latest AS base

LABEL maintainer="agentic-skills"
LABEL description="OpenCode Serve — Agentic Skills Platform with OpenAPI Agent and Nokia NetOps skills"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install OpenCode
RUN curl -fsSL https://opencode.ai/install | bash \
    && mv /root/.local/bin/opencode /usr/local/bin/opencode || true

# Set working directory
WORKDIR /app

# Copy project files
COPY opencode.json .
COPY AGENTS.md .
COPY .opencode/ .opencode/
COPY scripts/ scripts/
COPY specs/ specs/
COPY ingest/ ingest/

# Create output directory
RUN mkdir -p output data/chromadb

# Install Python dependencies for ChromaDB ingestion
RUN python3 -m venv /app/.venv \
    && /app/.venv/bin/pip install --no-cache-dir -r ingest/requirements.txt

# Make scripts executable
RUN chmod +x scripts/call-agent.sh scripts/query-kb.py ingest/ingest.py

# Environment
ENV PATH="/app/.venv/bin:/usr/local/bin:$PATH"
ENV OPENCODE_DISABLE_AUTOUPDATE=1

# Expose OpenCode serve port
EXPOSE 4096

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -sf http://localhost:4096/global/health || exit 1

# Default: start OpenCode in serve mode
CMD ["opencode", "serve", "--port", "4096", "--hostname", "0.0.0.0"]
