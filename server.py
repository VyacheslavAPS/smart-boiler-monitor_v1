import csv
from datetime import datetime
import os

from fastapi import FastAPI, Request
from pydantic import BaseModel

from weather_service import get_outdoor_temperature

app = FastAPI(title="Smart Boiler Monitor API")


@app.get("/")
def read_root():
    return {"status": "online", "system": "Smart Boiler Monitor"}


@app.get("/api/weather")
def read_weather():
    return get_outdoor_temperature()


class Telemetry(BaseModel):
    temps: dict
    power: dict
    pump: dict


DB_FILE = "heating_log.csv"

# Добавили t_outdoors в заголовки CSV
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "t_vhod",
            "t_vihod",
            "t_outdoors",
            "grid",
            "inverter",
            "pump_ok",
        ])


@app.post("/telemetry")
async def receive_telemetry(data: Telemetry):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Извлечение температур котла
    t_values = list(data.temps.values())
    t_in = t_values[0] if len(t_values) > 0 else 0
    t_out = t_values[1] if len(t_values) > 1 else 0

    # Автоматический забор уличной температуры из погодного сервиса
    weather_info = get_outdoor_temperature()
    t_outdoors = weather_info.get("temperature", 0.0)

    # Безопасное извлечение статусов
    grid = data.power.get("grid", False)
    inv = data.power.get("inv", False)
    pump_ok = data.pump.get("ok", False)

    # Запись всех данных в файл
    with open(DB_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([now, t_in, t_out, t_outdoors, grid, inv, pump_ok])

    print(
        f"[{now}] Вход: {t_in}°C, Выход: {t_out}°C, Улица: {t_outdoors}°C. Насос: {'OK' if pump_ok else 'ALARM'}"
    )
    return {"status": "success", "recorded_at": now}


@app.get("/status")
async def get_status():
    return {"server": "online", "database": DB_FILE}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)