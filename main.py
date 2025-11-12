import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Plot, VisitRequest

app = FastAPI(title="Plot Visit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Plot Visit API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Utility to convert ObjectId to string in documents

def serialize_doc(doc: dict):
    if not doc:
        return doc
    doc = dict(doc)
    _id = doc.get("_id")
    if isinstance(_id, ObjectId):
        doc["id"] = str(_id)
        del doc["_id"]
    return doc

# Seed some sample plots if collection empty
@app.post("/api/seed")
def seed_plots():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    count = db["plot"].count_documents({})
    if count > 0:
        return {"inserted": 0, "message": "Plots already exist"}
    samples = [
        {
            "title": "Sunset Meadows",
            "location": "Hillside Ave, Springfield",
            "size_sqft": 5400,
            "price_per_sqft": 12.5,
            "image_url": "https://images.unsplash.com/photo-1471623817296-1d290b868e9a?q=80&w=1200&auto=format&fit=crop",
            "description": "Gently sloping plot with beautiful sunset views."
        },
        {
            "title": "Riverside Greens",
            "location": "Oak River Rd, Rivertown",
            "size_sqft": 7200,
            "price_per_sqft": 15.0,
            "image_url": "https://images.unsplash.com/photo-1501706362039-c06b2d715385?q=80&w=1200&auto=format&fit=crop",
            "description": "Lush riverside land ideal for a family home."
        },
        {
            "title": "Cedar Ridge",
            "location": "Cedar Ridge Dr, Pineview",
            "size_sqft": 6000,
            "price_per_sqft": 13.75,
            "image_url": "https://images.unsplash.com/photo-1495107334309-fcf20504a5ab?q=80&w=1200&auto=format&fit=crop",
            "description": "Quiet neighborhood surrounded by cedars."
        }
    ]
    inserted_ids = []
    for s in samples:
        inserted_ids.append(create_document("plot", s))
    return {"inserted": len(inserted_ids), "ids": inserted_ids}

# List plots
@app.get("/api/plots")
def list_plots():
    docs = get_documents("plot")
    return [serialize_doc(d) for d in docs]

# Create a visit request
@app.post("/api/visit-requests")
def create_visit_request(payload: VisitRequest):
    # Validate that plot exists
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        plot_oid = ObjectId(payload.plot_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid plot_id")
    plot_exists = db["plot"].count_documents({"_id": plot_oid}) > 0
    if not plot_exists:
        raise HTTPException(status_code=404, detail="Plot not found")

    inserted_id = create_document("visitrequest", payload.model_dump())
    return {"id": inserted_id, "status": "ok"}

# List visit requests (limited)
@app.get("/api/visit-requests")
def list_visit_requests(limit: int = 50):
    docs = get_documents("visitrequest", limit=limit)
    return [serialize_doc(d) for d in docs]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
