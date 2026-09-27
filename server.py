from fastapi import FastAPI, Request
from datetime import datetime, timezone, timedelta
import requests

app = FastAPI()

# Aapka Firebase Realtime Database URL
FIREBASE_DB_URL = "https://duet-transit-sa-ui-default-rtdb.firebaseio.com"

PKT_TZ = timezone(timedelta(hours=5))

@app.api_route("/api/track", methods=["GET", "POST"])
async def receive_location(request: Request):
    data = {}
    try:
        data = await request.json()
    except Exception:
        pass

    if not data:
        try:
            form = await request.form()
            data = dict(form)
        except Exception:
            pass

    params = dict(request.query_params)

    lat = float(data.get("lat") or data.get("latitude") or params.get("lat") or params.get("latitude") or 0.0)
    lon = float(data.get("lon") or data.get("longitude") or params.get("lon") or params.get("longitude") or 0.0)
    
    raw_speed = float(data.get("speed") or params.get("speed") or 0.0)
    speed = round(raw_speed * 1.852, 2) if raw_speed > 0 else 0.0
    bearing = float(data.get("bearing") or data.get("course") or data.get("heading") or params.get("bearing") or 0.0)
    
    # Selected Point ID (Default: POINT_08)
    point_id = str(data.get("id") or params.get("id") or "POINT_08")
    now_pkt = datetime.now(PKT_TZ).strftime("%Y-%m-%d %I:%M:%S %p")

    payload = {
        "lat": lat,
        "lon": lon,
        "speed": speed,
        "bearing": bearing,
        "timestamp": now_pkt
    }

    # Cloud Firebase mein direct write karein
    try:
        url = f"{FIREBASE_DB_URL}/live_fleet/{point_id}.json"
        requests.put(url, json=payload, timeout=5)
        print(f"[{now_pkt}] Firebase Synced: {point_id} -> Lat: {lat}, Lon: {lon}")
    except Exception as e:
        print(f"Firebase Error: {e}")

    return {"status": "success", "point": point_id}