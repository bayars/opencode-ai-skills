FROM debian:bookworm-slim

LABEL maintainer="agentic-skills"
LABEL description="OpenCode Serve — Agentic Skills Platform with OpenAPI Agent and Nokia NetOps skills"

# Install system dependencies + Bun (required by OpenCode)
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    python3 \
    python3-pip \
    python3-venv \
    git \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Install OpenCode (installs to ~/.opencode/bin/)
RUN curl -fsSL https://opencode.ai/install | bash
ENV PATH="/root/.opencode/bin:$PATH"

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
