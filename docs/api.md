# API

Base URL: `/api/v1`

## Auth
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`

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

## Examples

### Login
```json
POST /api/v1/auth/login
{
  "email": "admin@marketmind.ai",
  "password": "secret"
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