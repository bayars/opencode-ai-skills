# {{App Name}} API Rules

> Copy this file to a new folder: `apps/<app-name>/RULES.md`

## Spec Location

- Path or URL to the OpenAPI spec: `<url-or-path>`

## Authentication

- Type: Bearer / API Key / Basic / OAuth2
- Environment variable: `APP_NAME_API_KEY`
- Header format: `Authorization: Bearer $APP_NAME_API_KEY`

## Base URL

- Production: `https://api.example.com/v1`
- Sandbox: `https://sandbox.api.example.com/v1`

## Common Workflows

### Workflow 1: <Name>

1. Step one — `GET /endpoint`
2. Step two — `POST /endpoint`

## Pagination

- Style: cursor / offset / page
- Parameter: `cursor` or `page` + `per_page`

## Rate Limits

- Requests per minute: X
- Strategy: exponential backoff

## Known Quirks

- List any non-obvious behavior, required headers, field formats, etc.
