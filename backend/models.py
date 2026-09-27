from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime
from backend.database import Base


class RecyclingBin(Base):
 
    __tablename__ = "recycling_bins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, index=True)
    district = Column(String(80), nullable=False, default="Merkez")
    waste_type = Column(String(50), nullable=False, default="Plastik & Metal")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    fill_level_percentage = Column(Integer, nullable=False, default=0)
    capacity_liters = Column(Integer, nullable=False, default=1100)
    battery_percentage = Column(Integer, nullable=False, default=100)
    status = Column(String(30), nullable=False, default="OK")
    last_emptied = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def update_status_by_fill(self):
        if self.fill_level_percentage >= 80:
            self.status = "CRITICAL"
        elif self.fill_level_percentage >= 50:
            self.status = "WARNING"
        else:
            self.status = "OK"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "district": self.district,
            "waste_type": self.waste_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "fill_level_percentage": self.fill_level_percentage,
            "capacity_liters": self.capacity_liters,
            "battery_percentage": self.battery_percentage,
            "status": self.status,
            "last_emptied": self.last_emptied.isoformat() if self.last_emptied else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }
