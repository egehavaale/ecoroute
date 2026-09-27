from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from backend.models import RecyclingBin

BURSA_DEPOT = {
    "name": "Bursa Büyükşehir Atık Transfer & Lojistik Merkezi",
    "district": "Osmangazi",
    "latitude": 40.2050,
    "longitude": 29.0200,
    "role": "MUNICIPAL_DEPOT"
}

INITIAL_BINS = [
    {
        "name": "Heykel Tarihi Belediye Önü",
        "district": "Osmangazi",
        "waste_type": "Plastik & Metal",
        "latitude": 40.1828,
        "longitude": 29.0632,
        "fill_level_percentage": 88,
        "capacity_liters": 1100,
        "battery_percentage": 94,
    },
    {
        "name": "FSM Bulvarı Park Girişi",
        "district": "Nilüfer",
        "waste_type": "Kağıt & Karton",
        "latitude": 40.2115,
        "longitude": 28.9830,
        "fill_level_percentage": 92,
        "capacity_liters": 1100,
        "battery_percentage": 89,
    },
    {
        "name": "Zafer Plaza & Kent Meydanı",
        "district": "Osmangazi",
        "waste_type": "Elektronik & Batarya",
        "latitude": 40.1912,
        "longitude": 29.0577,
        "fill_level_percentage": 76,
        "capacity_liters": 800,
        "battery_percentage": 98,
    },
    {
        "name": "PodyumPark Yaşam Merkezi",
        "district": "Nilüfer",
        "waste_type": "Cam & Şişe",
        "latitude": 40.2230,
        "longitude": 28.9745,
        "fill_level_percentage": 84,
        "capacity_liters": 1100,
        "battery_percentage": 91,
    },
    {
        "name": "Yeşil Türbe & Emirsultan Meydanı",
        "district": "Yıldırım",
        "waste_type": "Plastik & Metal",
        "latitude": 40.1815,
        "longitude": 29.0745,
        "fill_level_percentage": 35,
        "capacity_liters": 1100,
        "battery_percentage": 100,
    },
    {
        "name": "Botanik Park Giriş Meydanı",
        "district": "Osmangazi",
        "waste_type": "Organik & Kompost",
        "latitude": 40.2150,
        "longitude": 29.0350,
        "fill_level_percentage": 45,
        "capacity_liters": 1100,
        "battery_percentage": 97,
    },
    {
        "name": "Görükle Üniversite Öğrenci Çarşısı",
        "district": "Nilüfer",
        "waste_type": "Kağıt & Karton",
        "latitude": 40.2255,
        "longitude": 28.8540,
        "fill_level_percentage": 95,
        "capacity_liters": 1500,
        "battery_percentage": 87,
    },
    {
        "name": "Merinos Atatürk Kongre Kültür Merkezi",
        "district": "Osmangazi",
        "waste_type": "Cam & Şişe",
        "latitude": 40.1985,
        "longitude": 29.0490,
        "fill_level_percentage": 25,
        "capacity_liters": 1100,
        "battery_percentage": 99,
    },
    {
        "name": "Ataevler Barış Mahallesi Meydanı",
        "district": "Nilüfer",
        "waste_type": "Plastik & Metal",
        "latitude": 40.2080,
        "longitude": 28.9560,
        "fill_level_percentage": 72,
        "capacity_liters": 1100,
        "battery_percentage": 92,
    },
    {
        "name": "Muradiye Külliyesi Parkı",
        "district": "Osmangazi",
        "waste_type": "Elektronik & Batarya",
        "latitude": 40.1930,
        "longitude": 29.0435,
        "fill_level_percentage": 18,
        "capacity_liters": 800,
        "battery_percentage": 96,
    }
]


def seed_recycling_bins(db: Session, force_reset: bool = False):

    from backend.database import engine, Base
    Base.metadata.create_all(bind=engine)

    existing_count = db.query(RecyclingBin).count()
    if existing_count > 0 and not force_reset:
        return existing_count

    if force_reset:
        db.query(RecyclingBin).delete()
        db.commit()

    now = datetime.now(timezone.utc)
    for idx, data in enumerate(INITIAL_BINS):
        bin_obj = RecyclingBin(
            name=data["name"],
            district=data["district"],
            waste_type=data["waste_type"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            fill_level_percentage=data["fill_level_percentage"],
            capacity_liters=data["capacity_liters"],
            battery_percentage=data["battery_percentage"],
            last_emptied=now - timedelta(days=(idx % 4) + 1, hours=idx * 2),
            last_updated=now
        )
        bin_obj.update_status_by_fill()
        db.add(bin_obj)

    db.commit()
    return len(INITIAL_BINS)
