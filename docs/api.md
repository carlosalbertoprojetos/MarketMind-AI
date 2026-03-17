# API

Base URL: `/api/v1`

## Auth
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`

### Headers
- `Authorization: Bearer <access_token>`

## Core Resources (CRUD)
- `/organizations`
- `/users`
- `/workspaces`
- `/brands`
- `/products`
- `/competitors`
- `/personas`
- `/campaigns`
- `/content-items`
- `/posts`
- `/media-assets`
- `/schedules`
- `/analytics/events`
- `/social-accounts`
- `/integrations`
- `/memberships`

## AI Endpoints
- `POST /ai/product/analyze`
- `POST /ai/market/analyze`
- `POST /ai/audience/generate`
- `POST /ai/narrative/generate`
- `POST /ai/content/generate`
- `POST /ai/campaign/plan`
- `GET /ai/analytics/summary`
- `POST /ai/pipeline/run`
- `GET /ai/pipeline/runs?product_id=<uuid>`
- `GET /ai/pipeline/runs/{run_id}`

## Examples

### Login
```json
POST /api/v1/auth/login
{
  "email": "admin@marketmind.ai",
  "password": "secret"
}
```

### Reset de senha (dev)
```json
POST /api/v1/auth/forgot-password
{
  "email": "admin@marketmind.ai"
}
```

```json
POST /api/v1/auth/reset-password
{
  "token": "<token>",
  "new_password": "nova-senha"
}
```

### Criar produto
```json
POST /api/v1/products
{
  "brand_id": "<uuid>",
  "name": "MarketMind",
  "description": "Marketing intelligence OS",
  "website_url": "https://example.com"
}
```

### Gerar conteudo
```json
POST /api/v1/ai/content/generate
{
  "product_id": "<uuid>",
  "content_type": "linkedin_post",
  "brief": "Explique o valor do produto para SaaS B2B"
}
```
