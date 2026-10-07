from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from data_generator import generate_demo_regions
from anomaly_engine import AnomalyReasoner, DiscoveryPassport

app = FastAPI(title="COSMIC-TRACE", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

demo_regions = generate_demo_regions()
reasoner = AnomalyReasoner()


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/regions")
def list_regions() -> Dict[str, Any]:
    return {"regions": [{"id": key, "name": region["name"], "description": region["discovery_story"]["headline"]} for key, region in demo_regions.items()]}


@app.get("/api/region/{region_id}")
def get_region(region_id: str) -> Dict[str, Any]:
    region = demo_regions.get(region_id)
    if not region:
        return {"error": "Region not found"}
    return region


@app.post("/api/analyze/object")
def analyze_object(region_id: str, object_id: str) -> Dict[str, Any]:
    region = demo_regions.get(region_id)
    if not region:
        return {"error": "Region not found"}

    object_epochs = []
    for epoch in region["epochs"]:
        source = next((s for s in epoch["sources"] if s["id"] == object_id), None)
        if source:
            object_epochs.append({"timestamp": epoch["timestamp"], "data": source})

    if not object_epochs:
        return {"error": "Object not found"}

    analysis = reasoner.analyze({"id": object_id, "epochs": object_epochs}, region)
    passport = DiscoveryPassport(object_id, {"id": object_id, "epochs": object_epochs}, analysis, region).to_dict()
    return {"object_id": object_id, "analysis": analysis, "passport": passport}


@app.get("/")
def landing() -> str:
    return ""  # static frontend handles root route


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
