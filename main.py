from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import os
from database import db, create_document, get_documents

app = FastAPI(title="BHAO.PK API", version="1.0.0")

# CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class Product(BaseModel):
    title: str
    price: float
    rating: Optional[float] = None
    store: Optional[str] = None
    image: Optional[str] = None
    badge: Optional[str] = None

class SearchRequest(BaseModel):
    q: Optional[str] = ""
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    sort: Optional[str] = "value"
    stores: Optional[List[str]] = None

@app.get("/")
async def root():
    return {"message": "BHAO.PK API ready"}

@app.get("/test")
async def test_db():
    status = {
        "backend": "ok",
        "database": "not-configured",
        "database_url": os.getenv("DATABASE_URL", "not set"),
        "database_name": os.getenv("DATABASE_NAME", "not set"),
        "connection_status": "disconnected",
        "collections": []
    }
    if db is not None:
        status["database"] = "ok"
        try:
            cols = await _list_collections()
            status["collections"] = cols
            status["connection_status"] = "connected"
        except Exception:
            status["connection_status"] = "connected"
    return status

async def _list_collections():
    return db.list_collection_names() if db is not None else []

@app.post("/search")
async def search_products(payload: SearchRequest):
    # This endpoint is ready for DB-backed search later; currently returns empty list
    # Frontend design focuses on static mock data; when real data is added, wire it here.
    filter_dict = {}
    if payload.q:
        filter_dict["title"] = {"$regex": payload.q, "$options": "i"}
    if payload.min_price is not None or payload.max_price is not None:
        price_q = {}
        if payload.min_price is not None:
            price_q["$gte"] = payload.min_price
        if payload.max_price is not None:
            price_q["$lte"] = payload.max_price
        filter_dict["price"] = price_q

    results = []
    try:
        if db is not None:
            docs = get_documents("product", filter_dict, limit=60)
            for d in docs:
                d["_id"] = str(d.get("_id"))
            results = docs
    except Exception:
        results = []

    return {"items": results}
