from run import logger
import os
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database import engine, Base, get_db, SessionLocal
from backend.models import RecyclingBin
from backend.schemas import (
    RecyclingBinResponse,
    RouteOptimizationResponse,
    DashboardStats,
)
from backend.seed_data import seed_recycling_bins, BURSA_DEPOT
from backend import crud
from backend.optimizer import optimize_collection_route


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seeded_count = seed_recycling_bins(db, force_reset=False)
        logger.info(f"[EcoRoute] Database initialized with {seeded_count} Bursa smart recycling points.")
    finally:
        db.close()
    yield


app = FastAPI(
    title="EcoRoute / UrbanEco Tracker API",
    description="Smart City IoT & Green Transition Waste Logistics Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/", summary="Root Dashboard Interface", include_in_schema=False)
async def serve_dashboard():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "project": "EcoRoute / UrbanEco Tracker",
        "status": "Active",
        "message": "Frontend static file not found. Visit /docs for API documentation.",
        "docs": "/docs"
    }



@app.get(
    "/api/bins",
    response_model=List[RecyclingBinResponse],
    summary="Tüm Konteynerleri Getir (List All Containers)",
    tags=["Recycling Bins"]
)
def list_recycling_bins(
    status: Optional[str] = Query(None, description="Duruma göre filtrele: OK, WARNING, CRITICAL"),
    waste_type: Optional[str] = Query(None, description="Atık türüne göre filtrele (örn. Plastik, Kağıt, Cam)"),
    db: Session = Depends(get_db)
):

    bins = crud.get_all_bins(db=db, status=status, waste_type=waste_type)
    return bins


@app.get(
    "/api/bins/{bin_id}",
    response_model=RecyclingBinResponse,
    summary="Tekil Konteyner Detayı (Get Single Container)",
    tags=["Recycling Bins"]
)
def get_single_bin(bin_id: int, db: Session = Depends(get_db)):
    bin_obj = crud.get_bin(db=db, bin_id=bin_id)
    if not bin_obj:
        raise HTTPException(status_code=404, detail=f"Konteyner ID {bin_id} bulunamadı.")
    return bin_obj


@app.post(
    "/api/bins/{bin_id}/empty",
    response_model=RecyclingBinResponse,
    summary="Konteyneri Boşalt (Empty Container)",
    tags=["Recycling Bins"]
)
def empty_recycling_bin(bin_id: int, db: Session = Depends(get_db)):
    emptied_bin = crud.empty_bin(db=db, bin_id=bin_id)
    if not emptied_bin:
        raise HTTPException(status_code=404, detail=f"Konteyner ID {bin_id} bulunamadı.")
    return emptied_bin



@app.get(
    "/api/route/optimize",
    response_model=RouteOptimizationResponse,
    summary="Optimize Toplama Rotası Üret (Generate Optimized Collection Route)",
    tags=["Smart Route Optimization"]
)
def get_optimized_route(
    threshold: int = Query(70, ge=10, le=100, description="Kritik doluluk eşiği yüzdesi (varsayılan: 70)"),
    db: Session = Depends(get_db)
):
    all_bins = db.query(RecyclingBin).all()
    candidate_bins = [b for b in all_bins if b.fill_level_percentage >= threshold]

    if not candidate_bins and all_bins:
        candidate_bins = sorted(all_bins, key=lambda b: b.fill_level_percentage, reverse=True)[:3]

    result = optimize_collection_route(candidate_bins=candidate_bins, depot=BURSA_DEPOT)
    result["threshold_used_percentage"] = threshold
    return result



@app.get(
    "/api/stats",
    response_model=DashboardStats,
    summary="Sistem KPI İstatistikleri (System KPI Statistics)",
    tags=["Dashboard Analytics"]
)
def get_system_stats(db: Session = Depends(get_db)):
    return crud.calculate_dashboard_stats(db=db)


@app.post(
    "/api/bins/simulate",
    response_model=List[RecyclingBinResponse],
    summary="IoT Sensör Doluluk Simülasyonu (Simulate IoT Telemetry Pulse)",
    tags=["Simulation & Testing"]
)
def simulate_iot_traffic(db: Session = Depends(get_db)):
   
    updated_bins = crud.simulate_iot_fill_fluctuation(db=db)
    return updated_bins


@app.post(
   
    summary="Veritabanını Sıfırla ve Yeniden Doldur (Reset & Reseed Initial Mock Data)",
    tags=["Simulation & Testing"]
)
def reset_and_seed(db: Session = Depends(get_db)):
    count = seed_recycling_bins(db=db, force_reset=True)
    return {
        "success": True,
        "message": f"Veritabanı {count} adet Bursa akıllı konteyner noktası ile başarıyla sıfırlandı.",
        "depot": BURSA_DEPOT
    }
