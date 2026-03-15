---
name: openapi-agent
description: "Interact with any application using its OpenAPI specification. Loads the spec, understands endpoints, and makes API calls following custom instructions."
---

# Skill: OpenAPI Agent

## Goal

Act as an intelligent API client for any application by reading its OpenAPI specification and executing API calls according to user instructions and application-specific rules.

## Use This Skill When

- The user wants to interact with an external application via its REST API
- The user provides or references an OpenAPI/Swagger specification
- The user asks to call, query, or automate actions against a specific API
- Another agent or n8n workflow sends a request to interact with an API

## Do Not Use This Skill When

- The user is asking about code in the local repository (use explore instead)
- The API has no OpenAPI spec available
- The user wants to build an API (not consume one)

## Inputs

- `spec_path` — Path or URL to the OpenAPI spec (JSON or YAML)
- `app_name` — Name of the target application (used to load app-specific rules)
- `action` — What the user wants to do (natural language description)
- `auth` — Authentication details (API key, bearer token, OAuth, etc.)

## Steps

1. **Load the OpenAPI spec** from the provided path or URL
2. **Load application-specific rules** from `.opencode/skills/openapi-agent/apps/<app_name>/RULES.md` if they exist
3. **Parse the spec** to understand available endpoints, methods, parameters, request/response schemas
4. **Match the user's intent** to the appropriate API endpoint(s)
5. **Construct the request** with correct path parameters, query parameters, headers, and body
6. **Execute the API call** using `curl` or the appropriate HTTP method
7. **Parse and present the response** in a structured, readable format
8. **Handle errors** by reading the error schema from the spec and suggesting fixes

## How to Add Application-Specific Rules

Create a rules file at:
```
.opencode/skills/openapi-agent/apps/<app_name>/RULES.md
```

This file should contain:
- Authentication instructions (how to get and use tokens)
- Common workflows (multi-step API sequences)
- Field mappings and business logic
- Rate limiting and pagination strategies
- Known quirks or workarounds

## Output

- The raw API response (formatted)
- A human-readable summary of what happened
- Next steps or related actions the user might want to take
