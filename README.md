# Smart AI Business Assistant Platform

Smart AI Business Assistant Platform is a compact AI operations dashboard. It combines grounded chat, document intelligence, lead capture, workflow automation, and analytics in one practical system.

## Quick Start

### Local Development (5 minutes)

1. **Install Python dependencies:**
   ```bash
   pip install -r backend/requirements-web.txt
   ```

2. **Create `.env` file** in repo root:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/smart_ai
   SECRET_KEY=dev-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **Start backend** (Terminal 1):
   ```bash
   python run_backend.py
   ```
   Backend runs on http://localhost:8000

4. **Start frontend** (Terminal 2):
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Frontend runs on http://localhost:8080

5. **Test the API:**
   ```bash
   curl http://localhost:8000/api/health
   ```

### Production Deployment (Render + Supabase + Vercel)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete step-by-step instructions.

**In short:**
1. Create Supabase PostgreSQL database
2. Create Render web service (connects to GitHub, auto-deploys on push)
3. Set `DATABASE_URL` and `SECRET_KEY` in Render environment
4. Deploy frontend to Vercel
5. Update `API_BASE` in [frontend/app.js](frontend/app.js)

## Features

- **Authentication**: JWT-based login/signup
- **AI Chat**: Grounded conversations with document context (RAG)
- **Document Upload**: PDF text extraction and semantic search
- **Lead Management**: Capture and track leads with scoring
- **Workflows**: Automated email summaries and CRM sync
- **Analytics**: Real-time dashboard with conversation/lead/workflow metrics
- **Audit Logs**: Full activity history for compliance

## Architecture

```
┌──────────────────┐
│   Frontend       │ ← Vercel or local HTTP server
│  (HTML/JS/CSS)   │
└────────┬─────────┘
         │ API calls
┌────────▼──────────────────┐
│   Backend (FastAPI)       │ ← Render or local
│ ├─ Auth/JWT               │
│ ├─ Chat + RAG             │
│ ├─ Documents + PDF        │
│ ├─ Leads + Scoring        │
│ ├─ Workflows              │
│ └─ Analytics              │
└────────┬──────────────────┘
         │ SQL
┌────────▼──────────────────┐
│   Database (PostgreSQL)   │ ← Supabase or local
│  ├─ users                 │
│  ├─ conversations         │
│  ├─ documents             │
│  ├─ leads                 │
│  ├─ workflows             │
│  └─ audit_logs            │
└──────────────────────────┘
```

## Core Components

### Backend (FastAPI)
- **`app/main.py`**: FastAPI app initialization
- **`app/core/config.py`**: Environment configuration (auto-normalizes DATABASE_URL)
- **`app/db/session.py`**: Async database connection pool
- **`app/models/`**: SQLAlchemy ORM models (users, conversations, documents, etc.)
- **`app/schemas/`**: Pydantic request/response validation
- **`app/api/routes/`**: API endpoints (auth, chat, docs, leads, workflows, analytics)
- **`app/services/`**: Business logic
  - `rag.py`: ChromaDB vector store (lazy-loaded)
  - `agents.py`: AI/LLM integration (pluggable)
  - `users.py`: User management
  - `leads.py`: Lead scoring and routing
  - `workflows.py`: Automation execution
  - `analytics.py`: Metrics calculation

### Frontend (Vanilla JS)
- **`index.html`**: Main page with UI framework
- **`app.js`**: App logic, API client, state management
- **`styles.css`**: Styling
- **`assets/`**: Images and static files

### Database (PostgreSQL)
- **`users`**: User accounts and auth
- **`conversations`**: Chat session metadata
- **`messages`**: Chat messages with roles (user/assistant)
- **`documents`**: Uploaded PDFs metadata
- **`leads`**: Lead records with scoring
- **`workflows`**: Workflow definitions and executions
- **`audit_logs`**: Complete activity history

## Dependencies

### Production (`requirements.txt`)
- **fastapi==0.125.0**: Web framework
- **uvicorn[standard]==0.23.2**: ASGI server
- **SQLAlchemy==2.0.35**: ORM
- **asyncpg==0.31.0**: PostgreSQL async driver
- **pydantic==1.10.13**: Data validation
- **bcrypt==3.2.2**: Password hashing
- **pypdf==4.1.1**: PDF text extraction
- **psycopg2-binary==2.9.10**: PostgreSQL compatibility
- All other packages pinned to specific versions

### Local Development (`requirements-web.txt`)
Same as production, but allows for easier updates.

### Optional (Lazy-Loaded)
- **chromadb**: Vector database for RAG (installed on demand)
- **sentence-transformers**: ML embeddings (installed on demand)

## Environment Variables

### Required for Production
- `DATABASE_URL`: PostgreSQL connection string with `postgresql+asyncpg://` format
- `SECRET_KEY`: Random 32+ character string for JWT signing
- `ALGORITHM`: JWT algorithm (default: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token lifetime (default: `30`)

### Optional
- `CHROMA_PATH`: ChromaDB storage path (default: `./chroma_store_v1`)
- `FRONTEND_DIR`: Path to frontend files (default: `../frontend`)
- `ALLOW_ORIGINS`: CORS origins (default: `*`)
- `OLLAMA_URL`: Ollama LLM endpoint (if using local LLM)
- `OLLAMA_MODEL`: Model name (if using Ollama)
- `OLLAMA_TIMEOUT_SECONDS`: Request timeout (default: `30`)

## Database Schema

All tables auto-created by SQLAlchemy on first run. Key models:

- **User**: `id`, `email`, `username`, `password_hash`, `created_at`
- **Conversation**: `id`, `user_id`, `created_at`, `updated_at`
- **Message**: `id`, `conversation_id`, `role` (user/assistant), `content`, `created_at`
- **Document**: `id`, `user_id`, `filename`, `content`, `created_at`
- **Lead**: `id`, `user_id`, `name`, `email`, `score`, `source`, `created_at`
- **Workflow**: `id`, `user_id`, `name`, `status`, `created_at`, `executed_at`
- **AuditLog**: `id`, `user_id`, `action`, `target`, `created_at`

## Deployment

### Render + Supabase + Vercel (Recommended)
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed setup.

### Docker (Local)
```bash
docker-compose up --build
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token

### Chat
- `POST /api/chat` - Send message
- `GET /api/conversations` - List conversations
- `GET /api/conversations/{id}` - Get conversation history

### Documents
- `POST /api/documents/upload` - Upload PDF
- `DELETE /api/documents/{id}` - Delete document

### Leads
- `POST /api/leads` - Create lead
- `GET /api/leads` - List leads
- `PUT /api/leads/{id}` - Update lead

### Workflows
- `POST /api/workflows` - Create workflow
- `GET /api/workflows` - List workflows

### Analytics
- `GET /api/analytics/summary` - Dashboard metrics

### Health
- `GET /api/health` - Service health check

## Troubleshooting

### Local Development

**Import errors:**
```bash
# Make sure you're in the right directory
cd <repo-root>
python run_backend.py
```

**Database connection errors:**
- Verify DATABASE_URL format: `postgresql+asyncpg://...`
- Check PostgreSQL is running locally

**Frontend can't reach backend:**
- Backend must be running on http://localhost:8000
- Check browser console (F12) for CORS errors

### Production (Render)

**psycopg2 import error:**
- DATABASE_URL must have `postgresql+asyncpg://` (not `postgresql://`)

**Port binding error:**
- Render sets the `$PORT` environment variable
- Dockerfile CMD respects this: `--port ${PORT:-8000}`

**Out of memory:**
- Current setup minimizes memory with lazy-loading
- Upgrade Render instance if needed
- Or install chromadb locally only

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for more troubleshooting.

## Project Structure

```
.
├── backend/
│   ├── Dockerfile              ← Docker image definition
│   ├── requirements.txt        ← Production dependencies (pinned)
│   ├── requirements-web.txt    ← Local dev dependencies
│   ├── app/
│   │   ├── main.py
│   │   ├── core/config.py
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/routes/
│   │   ├── services/
│   │   └── utils/
│   └── chroma_store_v1/        ← Vector DB storage
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   └── assets/
│
├── run_backend.py              ← Local startup script
├── docker-compose.yml          ← Docker Compose config
├── DEPLOYMENT_GUIDE.md         ← Production deployment steps
└── README.md                   ← This file
```

## Support

- Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for hosting questions
- Review error logs in browser console (frontend) and Render logs (backend)
- Verify environment variables are set correctly
- Test API health: `curl http://localhost:8000/api/health`
- PostgreSQL on Neon, Supabase, or Render PostgreSQL

The full step-by-step deployment instructions are in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

## Demo Flow
1. Create an account and log in.
2. Show the overview dashboard and live metrics.
3. Upload a document and ask a grounded question.
4. Create a lead and show the score or status.
5. Run a workflow and review the logs.
6. Show audit entries and document management.

## Project Structure
```text
backend/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
frontend/
  index.html
  styles.css
  app.js
```

## Practical Notes
- The app runs fully locally with Docker Compose.
- For production, use a hosted PostgreSQL database and persistent storage for durable data.
- The frontend can be pointed to any backend URL from its built-in API settings.
- If Ollama is unavailable, the assistant falls back safely.

## License
MIT
