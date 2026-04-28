from fastapi import FastAPI, HTTPException
import time
from sqlalchemy.exc import OperationalError
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine
from routes import auth, billing, stripe_webhook, admin
from core.config import settings
import redis


app = FastAPI(title="Subscription Billing API")

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(stripe_webhook.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Billing API running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    # check DB
    try:
        conn = engine.connect()
        conn.close()
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")

    # check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
    except Exception:
        raise HTTPException(status_code=503, detail="redis unavailable")

    return {"status": "ready"}