# Petstore API Rules

## Spec Location

- URL: `https://petstore3.swagger.io/api/v3/openapi.json`

## Authentication

- Type: API Key
- Header: `api_key: special-key`

## Base URL

- `https://petstore3.swagger.io/api/v3`

## Common Workflows

### List available pets
1. `GET /pet/findByStatus?status=available`

### Add a new pet
1. `POST /pet` — required fields: `name`, `photoUrls` (can be empty array)

### Purchase flow
1. `GET /pet/{petId}` — check pet details
2. `POST /store/order` — place order with petId, quantity, shipDate
3. `GET /store/order/{orderId}` — check order status

## Known Quirks

- `photoUrls` is required on pet creation even if empty array
- Pet status must be one of: `available`, `pending`, `sold`
