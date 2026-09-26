# EcoRoute — Urban Waste Telemetry & Route Optimization

A lightweight, full-stack decision support platform that simulates IoT waste container telemetry, visualizes bin capacity on interactive maps, and calculates fuel-efficient collection routes using heuristic Traveling Salesperson Problem (TSP) optimization.

---

## Technical Overview

Traditional waste management relies on fixed collection schedules regardless of bin fill status. This results in unnecessary fuel consumption, increased carbon emissions,  and operational inefficiency.

**EcoRoute** addresses this by:
1. Monitoring real-time fill levels via simulated ultrasonic IoT sensors.
2. Filtering containers exceeding a critical fill threshold (default: 70%).
3. Generating an optimized pickup sequence starting from a central depot using a Nearest-Neighbor TSP algorithm and the Haversine distance formula.

---

## System Architecture

```text
+-----------------------------------------------------------------------------------+
|                            ECOROUTE ARCHITECTURE                                 |
+-----------------------------------------------------------------------------------+

       [ IoT Bins / Telemetry Simulator ]
        (Ultrasonic Fill Level & GPS)
                   |
                   v (HTTP POST /api/bins/simulate)
+-----------------------------------------------------------------------------------+
|                        FASTAPI REST BACKEND (Python 3.11+)                        |
|                                                                                   |
|  +------------------------+  +--------------------------+  +-------------------+  |
|  |   API Router Endpoints |  |   Route Optimizer Engine |  |  Seed & Telemetry |  |
|  | - GET  /api/bins       |  |  - Haversine Distance    |  |  - Bursa Pilot    |  |
|  | - POST /api/bins/{id}  |  |  - TSP Nearest-Neighbor  |  |    Coordinates    |  |
|  | - GET  /api/route/...  |  |  - Emissions Calculations|  |  - Dynamic Jitter |  |
|  +------------------------+  +--------------------------+  +-------------------+  |
|                                       |                                           |
|                                       v (SQLAlchemy ORM 2.0)                      |
|                      +----------------------------------+                         |
|                      |   SQLite / PostgreSQL Database    |                         |
|                      +----------------------------------+                         |
+-----------------------------------------------------------------------------------+
                                        |
                          (JSON Payload / Static Assets)
                                        v
+-----------------------------------------------------------------------------------+
|                        FRONTEND SPA DASHBOARD                                     |
|                                                                                   |
|  +------------------------+  +--------------------------+  +-------------------+  |
|  | Tailwind CSS (Dark UI) |  |   Leaflet.js Map Engine  |  | KPI Metrics Cards |  |
|  | - Responsive Layout    |  | - OpenStreetMap Tiles    |  | - Avg Fill Level  |  |
|  | - Clean Analytics      |  | - Dynamic Waypoints      |  | - Urgent Bins     |  |
|  | - Real-time Status     |  | - Animated Route Line    |  | - Estimated Savings| |
|  +------------------------+  +--------------------------+  +-------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## Tech Stack

### Backend
* **Python 3.11+ / FastAPI:** Asynchronous REST API architecture with automatic OpenAPI documentation.
* **SQLAlchemy 2.0:** Relational ORM supporting SQLite and PostgreSQL environments.
* **Pydantic v2:** Data validation and schema enforcement.
* **Uvicorn:** ASGI server implementation.

### Frontend
* **Vanilla JavaScript (ES6+):** Dependency-free client-side logic.
* **Tailwind CSS:** Modern dark interface layout.
* **Leaflet.js:** OpenStreetMap tile integration and route rendering.

---

## API Documentation

| Method | Endpoint | Parameters | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | - | Serves the main SPA Dashboard interface. |
| `GET` | `/api/bins` | `status`, `waste_type` | Returns a list of all bins and their telemetry data. |
| `GET` | `/api/bins/{id}` | `id` (path) | Returns detailed status for a specific container. |
| `POST` | `/api/bins/{id}/empty` | `id` (path) | Resets bin fill percentage to 0%. |
| `GET` | `/api/route/optimize` | `threshold` (default: 70) | Calculates the optimized route for bins exceeding threshold. |
| `GET` | `/api/stats` | - | Serves summary metrics for KPI displays. |
| `POST` | `/api/bins/simulate` | - | Triggers simulated telemetry updates across bins. |
| `POST` | `/api/bins/seed` | - | Resets the database with seed coordinates in Bursa. |
| `GET` | `/docs` | - | Interactive Swagger UI API documentation. |

---

## Installation & Setup

### Requirements
* Python 3.10+
* `pip` package manager

### Local Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/ecoroute.git
   cd ecoroute
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Linux / macOS:
   python3 -m venv venv
   source venv/bin/activate

   # Windows:
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python run.py
   ```
   *Or directly via Uvicorn:*
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

5. **Access points:**
   * **Dashboard UI:** `http://localhost:8000`
   * **Swagger Docs:** `http://localhost:8000/docs`

---

## Optimization Logic

1. **Haversine Distance Formula:**
   Calculates the great-circle distance between two GPS points on Earth:
   $$d = 2R \cdot \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
   *(where $R = 6371$ km).*

2. **Nearest-Neighbor TSP Heuristic:**
   * **Origin:** Municipal Logistics Center (`40.2050, 29.0200`).
   * **Process:** Iteratively selects the nearest unvisited bin exceeding the critical capacity threshold.
   * **Return:** Appends the depot as the final waypoint once all critical locations are serviced.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.