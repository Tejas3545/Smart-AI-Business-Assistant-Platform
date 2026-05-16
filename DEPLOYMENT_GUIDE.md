# Deployment Guide

This project is easiest to host as two parts:

- Frontend: Vercel
- Backend: Render Web Service
- Database: Hosted PostgreSQL such as Neon, Supabase, or Render PostgreSQL

The frontend is static HTML/CSS/JS, so Vercel is a correct choice. The backend is a FastAPI service, so it must run on a server platform such as Render.

## 1. What goes where

### Frontend on Vercel

Deploy the `frontend/` folder as a static site.

You do not need frontend environment variables for this app.

After deployment, open the app and use the built-in `API Settings` panel to point the frontend at your backend URL.

### Backend on Render

Deploy the FastAPI backend using the Dockerfile in `backend/Dockerfile`.

Important: the Docker build context must be the repository root, because the Dockerfile copies files from `backend/`.

### Database

Use a hosted PostgreSQL database.

Do not rely on the free container filesystem for your main data if you want it to persist across restarts.

## 2. Backend environment variables

Create a `.env` file for the backend service with these values.

### Minimal production `.env`

```env
DATABASE_URL=postgresql+asyncpg://YOUR_DB_USER:YOUR_DB_PASSWORD@YOUR_DB_HOST:5432/YOUR_DB_NAME?sslmode=require
JWT_SECRET=replace-this-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
CHROMA_PATH=./chroma_store_v1
FRONTEND_DIR=../frontend
ALLOW_ORIGINS=https://YOUR_FRONTEND_DOMAIN,http://localhost:8080,http://localhost:5173
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_TIMEOUT_SECONDS=30
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