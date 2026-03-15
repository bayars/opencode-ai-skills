# Agentic Skills Platform

This project provides agentic skills hosted via OpenCode's serve API, callable from other agents, n8n workflows, or direct HTTP.

## Architecture

```
User / n8n / External Agent
        │
   HTTP Request
        ▼
  OpenCode Serve (:4096)
        │
        ├── api-agent ──────── openapi-agent skill ──── External APIs
        │                        └── apps/*/RULES.md
        │
        └── nokia-netops-agent ── nokia-netops skill
                                    └── ChromaDB (Nokia docs)
                                    └── Config generation
                                    └── Containerlab topology
```

## Skills

### openapi-agent
Reads any OpenAPI spec + app-specific rules, calls the right endpoints.
- Add new apps: `.opencode/skills/openapi-agent/apps/<name>/RULES.md`

### nokia-netops
Generates Nokia SR Linux / SR OS configs and Containerlab topologies.
- Knowledge base: ChromaDB populated from official Nokia documentation
- Ingest docs: `python3 ingest/ingest.py`
- Query KB: `python3 scripts/query-kb.py --query "BGP config"`

## Quick Start

```bash
# 1. Ingest Nokia docs into ChromaDB
pip install -r ingest/requirements.txt
python3 ingest/ingest.py

# 2. Start the server
opencode serve --port 4096

# 3. Call an agent
./scripts/call-agent.sh nokia-netops-agent "Configure 5 SROS routers with eBGP full mesh and generate containerlab topology"
./scripts/call-agent.sh api-agent "List all available pets from petstore"
```

## Calling via HTTP

```bash
# Create session
curl -X POST http://localhost:4096/session -H "Content-Type: application/json" -d '{"title": "task"}'

# Send to agent
curl -X POST http://localhost:4096/session/{id}/message -H "Content-Type: application/json" \
  -d '{"agent": "nokia-netops-agent", "parts": [{"type": "text", "text": "Configure 3 SR Linux leaves with eBGP to 2 SROS spines, generate containerlab topology"}]}'
```
