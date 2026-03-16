# Architecture

## Overview
CONTENT INTELLIGENCE OS e uma plataforma SaaS multi-tenant com camadas claras: Frontend, Backend API, AI Engine, Async Workers, Database, Vector Database e Infraestrutura.

## Layers
- Frontend: Next.js + React + TypeScript + Tailwind + Recharts.
- Backend API: FastAPI + SQLAlchemy + PostgreSQL (pgvector).
- AI Engine: agentes e servicos de inteligencia (produto, mercado, audiencia, narrativa, conteudo, campanha, analytics).
- Async Workers: Celery + Redis.
- Storage: S3 compativel (preparado).
- Infra: Docker e Docker Compose.

## Multi-Tenancy
- Todas as entidades operacionais incluem `organization_id`.
- O backend filtra dados por `organization_id` via dependencias de autenticacao.

## Core Domains
- Organizations, Users, Memberships, Workspaces
- Brands, Products, Competitors, Personas
- Campaigns, Content Items, Posts, Media Assets, Schedules
- Analytics Events, Social Accounts, Integrations

## Auth
- JWT access token + refresh token.
- Password hashing com bcrypt.
- Roles (via memberships): admin, editor, viewer.

## AI Pipeline (Atual)
- Product Intelligence: extrai features, beneficios, proposta de valor.
- Market Intelligence: mapa competitivo.
- Audience Intelligence: gera personas.
- Narrative Engine: estrutura narrativa (problem, diagnosis, solution, proof, CTA).
- Content Generation: gera variantes short/medium/long/technical/sales.
- Campaign Engine: cria campanhas por etapas.
- Analytics Engine: sumariza engagement/CTR/growth.

## Workers
- Celery tasks para: content generation, image generation, market analysis, scheduled posting.

## Data Flow (Exemplo)
1. Produto criado -> /products
2. Analise de produto -> /ai/product/analyze
3. Personas -> /ai/audience/generate
4. Narrativa -> /ai/narrative/generate
5. Conteudo -> /ai/content/generate
6. Campanha -> /ai/campaign/plan
7. Agendamento -> /schedules
8. Eventos -> /analytics/events

## Observacoes
- Crawlers e parsing estao preparados como estrutura, mas as integracoes reais sao futuras.
- Vector search via pgvector ja esta na modelagem (Product e ContentItem).