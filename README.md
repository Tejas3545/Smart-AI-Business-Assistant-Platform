# Smart AI Business Assistant Platform

Production-oriented MVP for the Imperion Data Systems assessment. This system combines an AI assistant, RAG document retrieval, lead capture, workflow automation, and an admin dashboard.

## Architecture Overview
- **Frontend**: Static dashboard (HTML/CSS/JS) served by Nginx or FastAPI.
- **Backend**: FastAPI with async SQLAlchemy + PostgreSQL.
- **RAG**: ChromaDB + Sentence Transformers embeddings (local, no external LLM).
- **Agents**: Planner, Executor, Validator pipeline (deterministic orchestration).
- **Auth**: JWT-based login/signup.

## Key Features
- Contextual assistant with multi-turn chat and grounded responses.
- Document upload with semantic chunking + vector retrieval.
- Short-term conversation memory stored in DB.
- Long-term user memory stored for personalization.
- Lead capture with hot/warm/cold scoring.
- Follow-up message generation for leads.
- Workflow automations: email summary, CRM sync, calendar booking.
- Admin dashboard for analytics and logs.
- Dockerized deployment with environment configuration.

## Setup (Docker)
```bash
cp .env.example .env

docker-compose up --build
```

- API: http://localhost:8000
- Dashboard (Nginx): http://localhost:8080
- Dashboard (FastAPI static): http://localhost:8000

## Hosting / Deployment
The simplest reliable deployment is a single Linux VPS or cloud VM running Docker Compose.

Recommended approach:
1. Provision an Ubuntu VM with Docker and Docker Compose installed.
2. Copy this repository to the server and create a production `.env` file.
3. Set `ALLOW_ORIGINS` to your deployed frontend domain and API domain.
4. Run `docker-compose up -d --build`.
5. Put Nginx or a cloud load balancer in front of the `ui` and `api` services if you want HTTPS.

Minimum environment variables for deployment:
- `DATABASE_URL`
- `JWT_SECRET`
- `CHROMA_PATH`
- `ALLOW_ORIGINS`
- `OLLAMA_URL` and `OLLAMA_MODEL` if you want local LLM support

If you use a managed hosting platform, keep the PostgreSQL volume and Chroma storage persistent, or the chat/doc memory will reset on restart.

## Architecture / Workflow
1. A user logs in or signs up with JWT auth.
2. Chat requests are routed through intent planning, grounded retrieval, and response validation.
3. Uploaded documents are parsed, chunked, embedded, and stored in ChromaDB.
4. Lead capture writes to PostgreSQL and updates user memory.
5. Workflow actions create run records and audit logs.
6. The dashboard reads analytics, activity logs, conversations, leads, workflows, and documents from the API.

## Local Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - JWT signing secret
- `CHROMA_PATH` - persistent path for ChromaDB
- `ALLOW_ORIGINS` - comma-separated CORS list

## Demo Flow
1. Create account and login.
2. Upload business documents (PDF or TXT).
3. Ask the assistant questions; responses are grounded in uploads.
4. Save leads and observe hot/warm/cold scoring.
5. Trigger automations and view logs.
6. Review dashboard analytics.

## Notes
- This MVP runs fully offline with a local embedding model.
- For production, swap the `llm_stub.py` with an LLM provider.
- Documents are stored in ChromaDB with metadata linking to SQL records.

## Suggested Demo Script (5 min)
1. Show login and dashboard KPIs.
2. Upload a doc and ask a question.
3. Capture a lead and show score.
4. Run a workflow automation.
5. Show analytics and logs.

## Project Structure
```
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

## License
MIT
