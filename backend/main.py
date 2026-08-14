import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models
from routers import products, orders, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Focus API")

# Comma-separated list of allowed origins, e.g:
# https://focus-storefront.onrender.com,https://focus-admin.onrender.com
origins_env = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in origins_env.split(",")] if origins_env != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "Focus API"}
