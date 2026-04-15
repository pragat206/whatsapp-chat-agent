# WhatsApp AI Agent Platform

A production-grade AI-powered WhatsApp chat agent platform built with Python FastAPI and React. Uses AiSensy as the WhatsApp BSP (Business Solution Provider) and provides a full admin dashboard for managing conversations, knowledge base, products, analytics, and team operations.

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   WhatsApp   │────▶│   AiSensy    │────▶│  FastAPI Backend │
│   End Users  │◀────│   (BSP)      │◀────│  + Celery Workers│
└──────────────┘     └──────────────┘     └───────┬──────────┘
                                                   │
                                          ┌────────┴────────┐
                                          │                 │
                                    ┌─────▼─────┐   ┌──────▼──────┐
                                    │ PostgreSQL │   │    Redis    │
                                    │ + pgvector │   │ (cache/queue)│
                                    └───────────┘   └─────────────┘
                                          │
                                    ┌─────▼─────┐
                                    │ React      │
                                    │ Dashboard  │
                                    └───────────┘
```

### Data Flow

1. **Inbound**: WhatsApp → AiSensy webhook → FastAPI → Message stored → AI/RAG pipeline → Response generated → AiSensy API → WhatsApp
2. **Outbound (manual)**: Dashboard → API → AiSensy API → WhatsApp
3. **Knowledge ingestion**: Upload → Parse → Chunk → Embed (OpenAI) → Store in pgvector

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0 |
| Database | PostgreSQL 16 + pgvector |
| Cache/Queue | Redis |
| Background Jobs | Celery |
| Auth | JWT with refresh tokens, bcrypt |
| LLM | OpenAI-compatible API (GPT-4o default) |
| Embeddings | text-embedding-3-small via pgvector |
| Frontend | React 18, Vite, TypeScript, Tailwind CSS |
| BSP | AiSensy (WhatsApp Business API) |
| Containerization | Docker + docker-compose |
| Reverse Proxy | Nginx |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Or: Python 3.11+, Node.js 20+, PostgreSQL 16 (with pgvector), Redis

### With Docker (recommended)

```bash
# 1. Clone and enter project
cd whatsapp-chat-agent

# 2. Set up environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# 3. Start all services
docker-compose up -d

# 4. Run migrations
docker-compose exec backend alembic upgrade head

# 5. Seed demo data
docker-compose exec backend python -m scripts.seed

# 6. Access the platform
# Dashboard: http://localhost:3000
# API docs:  http://localhost:8000/docs
# API:       http://localhost:8000/api/v1
```

### Without Docker (local development)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings

# Ensure PostgreSQL + pgvector and Redis are running
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev

# Celery worker (separate terminal)
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

### Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@example.com | admin123456 |
| Operator | operator@example.com | operator123456 |
| Analyst | analyst@example.com | analyst123456 |

## Project Structure

```
├── backend/
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── ai/               # LLM client, agent logic, prompts
│   │   ├── api/v1/endpoints/  # REST API routes
│   │   ├── core/              # Config, database, security, middleware
│   │   ├── integrations/      # AiSensy BSP adapter
│   │   ├── knowledge/         # Parser, chunker, embedder, retriever
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/          # Business logic services
│   │   ├── tasks/             # Celery background tasks
│   │   └── tests/             # pytest test suite
│   └── scripts/               # Seed data, utilities
├── frontend/
│   └── src/
│       ├── components/        # UI components (layout, cards, etc.)
│       ├── hooks/             # React hooks (auth, etc.)
│       ├── pages/             # Dashboard, Conversations, etc.
│       ├── services/          # API client
│       └── types/             # TypeScript type definitions
├── docker/
│   └── nginx/                 # Nginx reverse proxy config
└── docker-compose.yml
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Refresh token |
| GET | `/api/v1/auth/me` | Current user |
| GET/POST | `/api/v1/users` | List/create users |
| GET | `/api/v1/conversations` | List conversations |
| GET | `/api/v1/conversations/:id` | Conversation detail with messages |
| POST | `/api/v1/conversations/:id/handoff` | Initiate human handoff |
| POST | `/api/v1/conversations/:id/resume-ai` | Resume AI mode |
| POST | `/api/v1/conversations/:id/send` | Send manual reply |
| POST | `/api/v1/conversations/:id/notes` | Add internal note |
| GET/POST | `/api/v1/products` | Product catalog |
| POST | `/api/v1/knowledge/upload` | Upload document |
| POST | `/api/v1/knowledge/manual` | Manual knowledge entry |
| POST | `/api/v1/knowledge/:id/reindex` | Reindex source |
| GET | `/api/v1/analytics/kpis` | Dashboard KPIs |
| GET | `/api/v1/analytics/trends` | Conversation trends |
| GET/PUT | `/api/v1/settings` | Platform settings |
| GET | `/api/v1/audit-logs` | Audit trail |
| GET/POST | `/api/v1/webhook/aisensy` | AiSensy webhook |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/ready` | Readiness check |
| GET | `/api/v1/live` | Liveness check |
| GET | `/metrics` | Prometheus metrics |

## Dashboard Pages

1. **Dashboard** — KPI cards, trend charts, recent conversations
2. **Conversations** — List, search, filter, and manage conversations
3. **Conversation Detail** — Full transcript, reply box, handoff controls, notes, tags
4. **Products** — Product catalog management
5. **Knowledge Base** — Upload/manage documents, manual entries, reindexing
6. **Analytics** — Charts, trends, AI vs human breakdown, distribution
7. **Team** — User management, role assignment
8. **Settings** — Platform configuration
9. **Audit Logs** — Action audit trail

## AiSensy Integration

The AiSensy integration is behind a BSP abstraction layer (`app/integrations/aisensy/`):

- **Webhook handler**: Parses inbound messages and status updates
- **Client**: Sends outbound messages via AiSensy API
- **Provider interface**: `BSPProvider` abstract class for easy BSP swapping

**Setup**: Configure `AISENSY_API_KEY`, `AISENSY_PROJECT_ID`, and `AISENSY_WEBHOOK_SECRET` in `.env`. Point AiSensy's project webhook to `https://yourdomain.com/api/v1/webhook/aisensy`.

## AI Agent Behavior

- Responds based on uploaded product knowledge (RAG)
- Never invents prices, warranty, stock, or policy information
- Captures leads naturally (name, city, interest, budget)
- Escalates to human on low confidence, complaints, or explicit request
- Supports English + Hindi conversations
- Logs all LLM calls with token usage and latency

## Environment Variables

See `backend/.env.example` for all configuration options.

## Testing

```bash
cd backend
pytest app/tests/ -v
pytest app/tests/ --cov=app --cov-report=html
```

## Production Deployment

1. Set `APP_ENV=production` in `.env`
2. Use strong, unique values for `SECRET_KEY` and `JWT_SECRET_KEY`
3. Configure real `AISENSY_*` and `OPENAI_*` credentials
4. Set up S3-compatible storage for file uploads
5. Configure Sentry DSN for error tracking
6. Use the nginx profile: `docker-compose --profile production up -d`
7. Set up SSL/TLS termination (e.g., Cloudflare, Let's Encrypt)
8. Restrict `/metrics` and `/docs` endpoints in production

## License

Proprietary — Internal use only.
