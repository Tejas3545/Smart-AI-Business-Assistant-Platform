# Deployment Guide

## Overview

Your Smart AI Business Assistant Platform is ready to deploy with:

- **Frontend**: Vercel (static HTML/JS)
- **Backend**: Render Web Service (FastAPI + Docker)
- **Database**: Supabase PostgreSQL (or any hosted PostgreSQL)

## Backend Deployment (Render)

### Prerequisites
- Render account (https://render.com)
- Supabase account (https://supabase.com)
- GitHub repository with latest code pushed

### Step 1: Create Supabase Database

1. Go to https://supabase.com and create a new project
2. Wait for project to be ready (~5 minutes)
3. Go to **Settings → Database**
4. Copy the connection string:
   - Look for "Connection string" or "URI"
   - Should look like: `postgresql://postgres:password@host:5432/postgres`
   - **Important**: Change `postgresql://` to `postgresql+asyncpg://` at the start
   - Final URL should look like: `postgresql+asyncpg://postgres:password@host:5432/postgres?sslmode=require`

### Step 2: Deploy on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository

4. Configure the web service:
   - **Name**: `smart-ai-backend`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your deploy branch)
   - **Build Command**: (leave empty - Render auto-detects)
   - **Start Command**: (leave empty - Dockerfile CMD is used)
   - **Instance Type**: Standard or higher
   - **Plan**: Starter ($7/month) or Pro ($12/month)

5. **Environment Variables** tab, add:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:password@host:5432/postgres?sslmode=require
   SECRET_KEY=<generate-random-32-char-string>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

   To generate SECRET_KEY:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

6. Click **"Deploy"**
7. Wait 3-5 minutes for build to complete
8. Check logs for any errors

### Step 3: Verify Backend

Once deployed, test the health endpoint:
```bash
curl https://your-service-name.onrender.com/api/health
```

Expected response: `{"status": "healthy"}`

### Important Notes on Dependencies

**dependencies.txt contains ONLY essential packages:**
- fastapi, uvicorn, SQLAlchemy, asyncpg, pydantic, etc.

**Lazy-loaded packages** (to save memory):
- `chromadb` (vector database for RAG)
- `sentence-transformers` (ML embeddings)

**What this means:**
- ✅ Backend starts quickly (< 1GB RAM)
- ✅ PDF documents can be uploaded
- ⏳ RAG features (semantic search) load on first use (~5-10 seconds)
- ⚠️ If you need RAG immediately, install extra packages locally then push

**To enable RAG locally:**
```bash
pip install chromadb sentence-transformers numpy
```

## Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

Update [frontend/app.js](frontend/app.js) with your backend URL:
```javascript
// At the top of the file, find:
const API_BASE = 'https://your-service-name.onrender.com';
// or use localStorage for user configuration
```

### Step 2: Deploy to Vercel

1. Go to https://vercel.com
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Other (static site)
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
5. Click **"Deploy"**

### Step 3: Test Frontend

After deployment:
1. Open your Vercel frontend URL
2. Try to login (create account or use test credentials)
3. Test chat, document upload, leads, etc.
4. Check browser console (F12) for any errors

## Local Development

### Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements-web.txt
   ```

3. **Create `.env` file** in repo root:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/smart_ai
   SECRET_KEY=dev-secret-key-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Start backend:**
   ```bash
   python run_backend.py
   ```
   Backend runs on http://localhost:8000

5. **Start frontend** (new terminal):
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Frontend runs on http://localhost:8080

6. **Test the API:**
   ```bash
   curl http://localhost:8000/api/health
   ```

### Enable RAG Locally (Optional)

If you want to test document upload and semantic search:
```bash
pip install chromadb sentence-transformers numpy
```

Then restart the backend.

## Troubleshooting

### Backend won't start
- **psycopg2 import error**: DATABASE_URL must start with `postgresql+asyncpg://` (not `postgresql://`)
- **Connection refused**: Verify DATABASE_URL is correct in Render environment
- **Check Render logs**: dashboard.render.com → your service → "Logs" tab

### Frontend can't reach backend
- Check browser console (F12) for CORS errors
- Verify API_BASE in [frontend/app.js](frontend/app.js) is correct
- Ensure backend is fully deployed and healthy

### Out of memory on Render
- Current setup minimizes memory with lazy-loading
- If you need RAG features: upgrade to Standard or Pro instance
- Or disable RAG by not installing chromadb

### Database connection timeout
- Check Supabase connection string is correct
- Verify you copied `postgresql+asyncpg://` format
- Test locally: `psql "postgresql+asyncpg://user:pass@host/db"`

## Important: The DATABASE_URL Format

**❌ Wrong:**
```
postgresql://user:password@host:5432/database
```

**✅ Correct:**
```
postgresql+asyncpg://user:password@host:5432/database?sslmode=require
```

The `asyncpg` driver is required because FastAPI uses async database operations.

## Production Checklist

- [ ] Supabase database created and verified
- [ ] Backend deployed to Render with all env vars set
- [ ] `curl /api/health` returns 200 status
- [ ] Frontend deployed to Vercel
- [ ] Frontend API_BASE points to Render backend URL
- [ ] Can login and create account
- [ ] Can create chat conversation
- [ ] Can upload documents
- [ ] Render logs show no startup errors
- [ ] Database is accessible from backend

## File Reference

```
backend/
├── Dockerfile              ← Used by Render for Docker build
├── requirements.txt        ← Production dependencies (PINNED VERSIONS)
├── requirements-web.txt    ← Local development dependencies
├── app/main.py             ← FastAPI app entry point
├── core/config.py          ← Environment config (auto-normalizes DATABASE_URL)
├── db/session.py           ← Database connection pool
├── models/                 ← SQLAlchemy ORM models
├── schemas/                ← Pydantic validation schemas
├── services/rag.py         ← Lazy-loaded ChromaDB RAG
└── api/routes/             ← API endpoints

frontend/
├── app.js                  ← Main app (update API_BASE here)
├── index.html              ← Entry page
├── styles.css              ← Styling
└── assets/                 ← Images, etc.

run_backend.py             ← Local startup script (uses correct Python path)
DEPLOYMENT_GUIDE.md        ← This file
```

### What each variable means

- `DATABASE_URL`: connection string for your hosted PostgreSQL database.
- `JWT_SECRET`: secret key used to sign login tokens. Use a long random value.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: login token lifetime in minutes.
- `CHROMA_PATH`: path where Chroma stores vector data.
- `FRONTEND_DIR`: only needed if the backend serves the frontend locally.
- `ALLOW_ORIGINS`: allowed browser origins for CORS.
- `OLLAMA_URL`: URL of an Ollama server if you want local LLM support.
- `OLLAMA_MODEL`: Ollama model name.
- `OLLAMA_TIMEOUT_SECONDS`: timeout for Ollama calls.

## 3. Vercel + Render + Supabase (brief)

This is the recommended deployment path for your setup.

1. Create a Supabase project.
2. Copy the database connection string from Supabase.
3. Deploy the backend on Render using `backend/Dockerfile`.
4. Deploy the frontend on Vercel from the `frontend/` folder.
5. Set the frontend API base to the Render backend URL.

### Supabase settings

- Open Supabase dashboard > Project > Settings > Database.
- Copy the connection string under "Connection string".
- Convert it to AsyncPG format if needed:

```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@YOUR_DB_HOST:5432/postgres?sslmode=require
```

- Use `JWT_SECRET` as a strong random phrase.
- Use `CHROMA_PATH=./chroma_store_v1` and keep that path stable on Render.
- Set `ALLOW_ORIGINS` to your Vercel app URL plus local testing URLs.

### Render backend settings

- Service type: Web Service.
- Root Directory: leave blank (do not set to `backend`).
- Dockerfile path: `backend/Dockerfile`.
- Docker Build Context Directory: leave blank or set to `.`.
- Environment variables: define them in Render's dashboard (do not commit `.env` to GitHub).
- Choose a service region close to your users.
- If Render supports persistent disk, mount it for `./chroma_store_v1`.
- Copy the backend URL once deployment succeeds.

> If Render reports `open Dockerfile: no such file or directory`, the Dockerfile path is wrong; the correct path is `backend/Dockerfile`.
>
> If Render reports `backend/requirements.txt: not found` or `/backend: not found`, the build context is wrong; use the repo root as the build context.

### Vercel frontend settings

- Import the repo and set the root directory to `frontend`.
- Select "Other" or "Static Site" if prompted.
- Build command: leave blank.
- Output directory: leave blank or `.`.
- Deploy the site.
- Open the deployed frontend and enter the Render API URL in the built-in API Settings panel.

### Why this works

- Vercel hosts the static UI.
- Render runs the FastAPI API.
- Supabase provides managed PostgreSQL.

## 4. What to actually set for hosting

### If you use Vercel for the frontend

Set `ALLOW_ORIGINS` to include your Vercel domain.

Example:

```env
ALLOW_ORIGINS=https://smart-ai-assistant.vercel.app,http://localhost:8080,http://localhost:5173
```

### If you use a hosted PostgreSQL provider

Paste the provider's connection string into `DATABASE_URL`.

If the database provider requires SSL and the connection fails, keep `?sslmode=require` at the end of the URL.

### If you do not run Ollama anywhere

Leave the Ollama values at their defaults. The app will still work and fall back safely when the model endpoint is not reachable.

If you do run Ollama, point `OLLAMA_URL` to the machine where Ollama is running.

## 5. Step-by-step hosting process

### Step 1: Push the code to GitHub

Make sure the project is in a GitHub repository.

### Step 2: Create the database

Create a PostgreSQL database on a hosted provider.

Copy the connection string.

### Step 3: Deploy the backend on Render

1. Log in to Render.
2. Create a new Web Service.
3. Connect your GitHub repository.
4. Choose Docker deployment.
5. Keep the root/build context at the repository root.
6. Point Render to `backend/Dockerfile`.
7. Add the backend environment variables listed above.
8. Set `DATABASE_URL` to your hosted PostgreSQL string.
9. Set `JWT_SECRET` to a strong random secret.
10. Set `ALLOW_ORIGINS` to your Vercel URL.
11. Deploy the service.

### Step 4: Deploy the frontend on Vercel

1. Log in to Vercel.
2. Import the same GitHub repository.
3. Set the root directory to `frontend`.
4. Deploy as a static site.
5. Wait for the deployment to finish.

### Step 5: Connect the frontend to the backend

Open the Vercel site in your browser.

1. Click `API Settings`.
2. Enter the Render backend URL, for example `https://your-backend.onrender.com`.
3. Save it.

The frontend stores this value in the browser, so it will keep using the hosted backend after refreshes.

### Step 6: Test the app

Check these URLs first:

```text
https://YOUR_BACKEND_URL/api/health
https://YOUR_FRONTEND_URL/
```

Then test these actions in the frontend:

- sign up or log in
- refresh the dashboard
- upload a document
- send a chat message
- create a lead
- run a workflow
- confirm the activity logs update

## 5. Exact platform layout I recommend

If you want the simplest submission-ready setup, use this:

- Vercel for the frontend
- Render for the backend
- Neon or Supabase for PostgreSQL

That gives you a public frontend URL and a public backend URL with minimal manual infrastructure.

## 6. Local test before hosting

Before you deploy, verify locally:

```bash
cp .env.example .env
docker-compose up --build
```

Then open:

- `http://localhost:8080`
- `http://localhost:8000/api/health`

## 7. Common mistakes

- Using `frontend/` as the Render Docker build context. The backend Dockerfile expects the repository root.
- Leaving `ALLOW_ORIGINS` set to localhost only.
- Pointing the frontend at `http://localhost:8000` after deployment.
- Using a non-persistent local Chroma path when you expect data to survive restarts.
- Forgetting to replace `JWT_SECRET` with a real secret.

## 8. Short answer for each service

### Render backend `.env`

Use this shape:

```env
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
JWT_SECRET=some-long-random-secret
ALLOW_ORIGINS=https://YOUR_FRONTEND.vercel.app,http://localhost:8080,http://localhost:5173
CHROMA_PATH=./chroma_store_v1
ACCESS_TOKEN_EXPIRE_MINUTES=60
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_TIMEOUT_SECONDS=30
```

### Vercel frontend `.env`

None required for this app.

Set the backend URL from the app's Settings panel after deployment.

## 9. Final check

If the frontend opens on Vercel, the backend health endpoint returns `ok`, and login/chat/docs/leads/workflows work, then the hosting setup is correct.