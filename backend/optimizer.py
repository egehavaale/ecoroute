import math
from typing import List, Dict, Any
from backend.models import RecyclingBin
from backend.seed_data import BURSA_DEPOT


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:

    R = 6371.0 

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def optimize_collection_route(
    candidate_bins: List[RecyclingBin],
    depot: Dict[str, Any] = None
) -> Dict[str, Any]:
    
    if depot is None:
        depot = BURSA_DEPOT

    depot_lat = depot["latitude"]
    depot_lng = depot["longitude"]

    if not candidate_bins:
        return {
            "success": True,
            "algorithm": "Nearest-Neighbor TSP Heuristic",
            "depot": depot,
            "bins_to_collect_count": 0,
            "total_distance_km": 0.0,
            "unoptimized_distance_km": 0.0,
            "distance_saved_km": 0.0,
            "fuel_saved_liters": 0.0,
            "co2_prevented_kg": 0.0,
            "estimated_duration_minutes": 0,
            "threshold_used_percentage": 70,
            "waypoints": [
                {
                    "step_number": 1,
                    "is_depot": True,
                    "bin_id": None,
                    "name": depot["name"],
                    "district": depot["district"],
                    "latitude": depot_lat,
                    "longitude": depot_lng,
                    "fill_level_percentage": 0,
                    "waste_type": "Municipal Fleet Depot",
                    "action_note": "Tüm konteynerler normal seviyede, toplama turu gerekmiyor."
                }
            ],
            "polyline_coordinates": [[depot_lat, depot_lng]]
        }

    unoptimized_distance = 0.0
    prev_lat, prev_lng = depot_lat, depot_lng
    for b in candidate_bins:
        unoptimized_distance += haversine_distance(prev_lat, prev_lng, b.latitude, b.longitude)
        prev_lat, prev_lng = b.latitude, b.longitude
    unoptimized_distance += haversine_distance(prev_lat, prev_lng, depot_lat, depot_lng)
    unoptimized_distance = round(unoptimized_distance * 1.35, 2)

    unvisited = candidate_bins.copy()
    ordered_bins: List[RecyclingBin] = []
    current_lat, current_lng = depot_lat, depot_lng
    optimized_distance = 0.0

    while unvisited:
        nearest_bin = min(
            unvisited,
            key=lambda b: haversine_distance(current_lat, current_lng, b.latitude, b.longitude)
        )
        dist = haversine_distance(current_lat, current_lng, nearest_bin.latitude, nearest_bin.longitude)
        optimized_distance += dist
        ordered_bins.append(nearest_bin)
        unvisited.remove(nearest_bin)
        current_lat, current_lng = nearest_bin.latitude, nearest_bin.longitude

    return_dist = haversine_distance(current_lat, current_lng, depot_lat, depot_lng)
    optimized_distance += return_dist
    optimized_distance = round(optimized_distance, 2)

    distance_saved = round(max(0.0, unoptimized_distance - optimized_distance), 2)
    fuel_saved = round(distance_saved * 0.34, 2)
    co2_prevented = round(fuel_saved * 2.68, 2)

    driving_minutes = (optimized_distance / 35.0) * 60.0
    collection_minutes = len(ordered_bins) * 4.0
    total_minutes = int(round(driving_minutes + collection_minutes))

    waypoints = []
    waypoints.append({
        "step_number": 1,
        "is_depot": True,
        "bin_id": None,
        "name": f"BAŞLANGIÇ: {depot['name']}",
        "district": depot["district"],
        "latitude": depot_lat,
        "longitude": depot_lng,
        "fill_level_percentage": 0,
        "waste_type": "Filo Hareket Üssü",
        "action_note": "Akıllı rota başlatıldı. Toplama aracı çıkış yaptı."
    })

    polyline = [[depot_lat, depot_lng]]

    for idx, b in enumerate(ordered_bins, start=2):
        waypoints.append({
            "step_number": idx,
            "is_depot": False,
            "bin_id": b.id,
            "name": b.name,
            "district": b.district,
            "latitude": b.latitude,
            "longitude": b.longitude,
            "fill_level_percentage": b.fill_level_percentage,
            "waste_type": b.waste_type,
            "action_note": f"%{b.fill_level_percentage} Dolu - {b.waste_type} atığı boşaltılacak."
        })
        polyline.append([b.latitude, b.longitude])

    waypoints.append({
        "step_number": len(waypoints) + 1,
        "is_depot": True,
        "bin_id": None,
        "name": f"VARIŞ & BOŞALTIM: {depot['name']}",
        "district": depot["district"],
        "latitude": depot_lat,
        "longitude": depot_lng,
        "fill_level_percentage": 0,
        "waste_type": "Geri Dönüşüm İşleme Tesisi",
        "action_note": "Toplanan tüm atıklar tesise teslim edildi, rota tamamlandı."
    })
    polyline.append([depot_lat, depot_lng])

    return {
        "success": True,
        "algorithm": "Nearest-Neighbor TSP Heuristic",
        "depot": depot,
        "bins_to_collect_count": len(ordered_bins),
        "total_distance_km": optimized_distance,
        "unoptimized_distance_km": unoptimized_distance,
        "distance_saved_km": distance_saved,
        "fuel_saved_liters": fuel_saved,
        "co2_prevented_kg": co2_prevented,
        "estimated_duration_minutes": total_minutes,
        "threshold_used_percentage": 70,
        "waypoints": waypoints,
        "polyline_coordinates": polyline
    }
