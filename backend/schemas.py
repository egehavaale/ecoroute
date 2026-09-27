from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class RecyclingBinBase(BaseModel):
    name: str = Field(..., example="Heykel Meydanı Akıllı Ayrıştırma")
    district: str = Field("Osmangazi", example="Osmangazi")
    waste_type: str = Field("Plastik & Metal", example="Plastik & Metal")
    latitude: float = Field(..., example=40.1828)
    longitude: float = Field(..., example=29.0632)
    fill_level_percentage: int = Field(0, ge=0, le=100, example=85)
    capacity_liters: int = Field(1100, example=1100)
    battery_percentage: int = Field(100, ge=0, le=100, example=95)
    status: str = Field("OK", example="CRITICAL")


class RecyclingBinCreate(RecyclingBinBase):
    pass


class RecyclingBinUpdate(BaseModel):
    name: Optional[str] = None
    district: Optional[str] = None
    waste_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    fill_level_percentage: Optional[int] = Field(None, ge=0, le=100)
    capacity_liters: Optional[int] = None
    battery_percentage: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[str] = None


class RecyclingBinResponse(RecyclingBinBase):
    id: int
    last_emptied: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class Waypoint(BaseModel):
    step_number: int
    is_depot: bool = False
    bin_id: Optional[int] = None
    name: str
    district: str
    latitude: float
    longitude: float
    fill_level_percentage: int
    waste_type: Optional[str] = None
    action_note: str


class RouteOptimizationResponse(BaseModel):
    success: bool
    algorithm: str = "Nearest-Neighbor TSP Heuristic"
    depot: dict
    bins_to_collect_count: int
    total_distance_km: float
    unoptimized_distance_km: float
    distance_saved_km: float
    fuel_saved_liters: float
    co2_prevented_kg: float
    estimated_duration_minutes: int
    threshold_used_percentage: int
    waypoints: List[Waypoint]
    polyline_coordinates: List[List[float]]


class DashboardStats(BaseModel):
    total_bins: int
    critical_bins_count: int
    warning_bins_count: int
    ok_bins_count: int
    average_fill_level: float
    urgent_collection_needed: bool
    total_waste_in_system_liters: int
