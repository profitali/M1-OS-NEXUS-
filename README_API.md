Minimal Master API skeleton (FastAPI + Postgres)

Quick start (development)
1. Copy .env.example to .env and edit DATABASE_URL if needed.
2. Start Postgres:
   docker-compose up -d
3. Install dependencies:
   pip install -r requirements.txt
4. Create DB tables:
   python app/init_db.py
5. Run the app:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Endpoints (examples)
- GET  /health
- POST /auth/register  (email, password)
- POST /auth/token     (email, password) -> access_token (JWT)
- GET  /apps
- POST /apps
- POST /builds/apk
- GET  /builds/{id}

Notes
- This is a skeleton. For production: add migrations (Alembic), HTTPS, strong password policies, rate limits, and a job queue for builds (e.g., Celery/RQ).
