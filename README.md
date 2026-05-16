# Smart AI Business Assistant Platform

Smart AI Business Assistant Platform is a compact AI operations dashboard built for the Imperion Data Systems assessment. It combines grounded chat, document intelligence, lead capture, workflow automation, and analytics in one practical system that can run locally or be hosted with a simple production setup.

## Overview
The application is designed to demonstrate a realistic business assistant workflow rather than a toy chatbot. Users can log in, upload documents, ask grounded questions, capture leads, trigger automations, and monitor activity through a unified dashboard.

## Core Capabilities
- Grounded AI chat with document-aware responses.
- Document upload, chunking, embedding, and retrieval through ChromaDB.
- Lead capture with basic scoring and follow-up generation.
- Workflow execution for email summaries, CRM sync, and calendar booking.
- Dashboard analytics with conversations, messages, documents, workflows, and audit logs.
- JWT-based authentication with user sessions stored in PostgreSQL.

## Architecture
- Frontend: static HTML, CSS, and JavaScript.
- Backend: FastAPI with async SQLAlchemy.
- Database: PostgreSQL for users, leads, conversations, workflows, and audit history.
- Vector store: ChromaDB with Sentence Transformers embeddings.
- Deployment model: static frontend + API backend + persistent database.

## Local Setup
```bash
cp .env.example .env
docker-compose up --build
```

Then open:
- UI: http://localhost:8080
- API: http://localhost:8000
- Health check: http://localhost:8000/api/health

## Environment Variables
Use the `.env.example` file as the base. The important runtime values are:

- `DATABASE_URL` - PostgreSQL connection string.
- `JWT_SECRET` - long random value used to sign tokens.
- `ACCESS_TOKEN_EXPIRE_MINUTES` - token lifetime in minutes.
- `CHROMA_PATH` - persistent Chroma storage path.
- `FRONTEND_DIR` - local frontend path when the backend serves static files.
- `ALLOW_ORIGINS` - comma-separated CORS origins.
- `OLLAMA_URL` - optional Ollama endpoint if you want local LLM support.
- `OLLAMA_MODEL` - optional Ollama model name.
- `OLLAMA_TIMEOUT_SECONDS` - timeout for Ollama requests.

## Hosting
Recommended production layout:
- Frontend on Vercel
- Backend on Render
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
