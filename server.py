from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime
import csv
import os

app = FastAPI(title="Heating System Telemetry")


# Описываем структуру данных, которую ждем от ESP8266
class Telemetry(BaseModel):
    temps: dict
    power: dict
    pump: dict


# Имя файла для хранения истории
DB_FILE = r"C:\My projects\smart-boiler-monitor\heating_log.csv"

# Инициализируем CSV файл заголовками, если его еще нет
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "t_vhod", "t_vihod", "grid", "inverter", "pump_ok"])


@app.post("/telemetry")
async def receive_telemetry(data: Telemetry):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Извлекаем данные (адреса датчиков в ESP должны совпадать с ключами здесь)
    # Для примера берем первые два значения из словаря температур
    t_values = list(data.temps.values())
    t_in = t_values[0] if len(t_values) > 0 else 0
    t_out = t_values[1] if len(t_values) > 1 else 0

    # Записываем в лог
    with open(DB_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            now,
            t_in,
            t_out,
            data.power['grid'],
            data.power['inv'],
            data.pump['ok']
        ])

    print(f"[{now}] Данные получены: Вход {t_in}°C, Выход {t_out}°C. Статус: {'OK' if data.pump['ok'] else 'ALARM'}")
    return {"status": "success", "recorded_at": now}


@app.get("/status")
async def get_status():
    """Эндпоинт, чтобы просто проверить, жив ли сервер"""
    return {"server": "online", "database": DB_FILE}


if __name__ == "__main__":
    import uvicorn

    # Запуск сервера на порту 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)