import random
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models import RecyclingBin
from backend.schemas import DashboardStats


def get_all_bins(
    db: Session,
    status: Optional[str] = None,
    waste_type: Optional[str] = None
) -> List[RecyclingBin]:
    query = db.query(RecyclingBin)
    if status:
        query = query.filter(RecyclingBin.status == status.upper())
    if waste_type:
        query = query.filter(RecyclingBin.waste_type.ilike(f"%{waste_type}%"))
    return query.order_by(RecyclingBin.fill_level_percentage.desc()).all()


def get_bin(db: Session, bin_id: int) -> Optional[RecyclingBin]:
    return db.query(RecyclingBin).filter(RecyclingBin.id == bin_id).first()


def empty_bin(db: Session, bin_id: int) -> Optional[RecyclingBin]:

    bin_obj = get_bin(db, bin_id)
    if not bin_obj:
        return None

    now = datetime.now(timezone.utc)
    bin_obj.fill_level_percentage = 0
    bin_obj.status = "OK"
    bin_obj.last_emptied = now
    bin_obj.last_updated = now

    db.commit()
    db.refresh(bin_obj)
    return bin_obj


def simulate_iot_fill_fluctuation(db: Session) -> List[RecyclingBin]:
   
    bins = db.query(RecyclingBin).all()
    now = datetime.now(timezone.utc)

    for b in bins:
        if b.fill_level_percentage < 100:
            delta = random.choice([5, 8, 12, 15, 20])
            b.fill_level_percentage = min(100, b.fill_level_percentage + delta)
        b.update_status_by_fill()
        b.battery_percentage = max(70, b.battery_percentage - random.choice([0, 0, 1]))
        b.last_updated = now

    db.commit()
    return bins


def calculate_dashboard_stats(db: Session) -> DashboardStats:
    total_bins = db.query(RecyclingBin).count()
    if total_bins == 0:
        return DashboardStats(
            total_bins=0,
            critical_bins_count=0,
            warning_bins_count=0,
            ok_bins_count=0,
            average_fill_level=0.0,
            urgent_collection_needed=False,
            total_waste_in_system_liters=0
        )

    critical_count = db.query(RecyclingBin).filter(RecyclingBin.fill_level_percentage >= 80).count()
    warning_count = db.query(RecyclingBin).filter(
        RecyclingBin.fill_level_percentage >= 50,
        RecyclingBin.fill_level_percentage < 80
    ).count()
    ok_count = db.query(RecyclingBin).filter(RecyclingBin.fill_level_percentage < 50).count()

    avg_fill = db.query(func.avg(RecyclingBin.fill_level_percentage)).scalar() or 0.0

    all_bins = db.query(RecyclingBin).all()
    total_liters = sum(int(b.capacity_liters * (b.fill_level_percentage / 100.0)) for b in all_bins)

    return DashboardStats(
        total_bins=total_bins,
        critical_bins_count=critical_count,
        warning_bins_count=warning_count,
        ok_bins_count=ok_count,
        average_fill_level=round(float(avg_fill), 1),
        urgent_collection_needed=critical_count > 0,
        total_waste_in_system_liters=total_liters
    )
