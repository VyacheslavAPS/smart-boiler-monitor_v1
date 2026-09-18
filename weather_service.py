import re
import requests
from bs4 import BeautifulSoup

# Координаты для Open-Meteo (на примере Фастова)
LATITUDE = 50.0782
LONGITUDE = 29.9161

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
} # Имитация работы браузера


# --- Источник 1: Open-Meteo API (Основной) ---
def fetch_from_open_meteo() -> float | None:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data["current"]["temperature_2m"])
    except Exception:
        pass
    return None


# --- Источник 2: Sinoptik.ua (Резерв 1) ---
def fetch_from_sinoptik() -> float | None:
    url = "https://sinoptik.ua/погода-фастов"
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            temp_element = soup.select_one(".R1ENpvZz")
            if temp_element:
                # Извлекаем число (например, "+18°C" -> 18.0, "-3°C" -> -3.0)
                match = re.search(r"[-+]?\d+", temp_element.text)
                if match:
                    return float(match.group())
    except Exception:
        pass
    return None


# --- Источник 3: Meteofor.com.ua (Резерв 2) ---
def fetch_from_meteofor() -> float | None:
    url = "https://meteofor.com.ua/weather-fastiv-4948/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Находим блок с текущей температурой
            temp_element = soup.select_one(".temperature .unit_temperature_c")
            if temp_element:
                match = re.search(r"[-+]?\d+", temp_element.text)
                if match:
                    return float(match.group())
    except Exception:
        pass
    return None


# --- Основная функция с отказоустойчивостью (Failover) ---
def get_outdoor_temperature() -> dict:
    sources = [
        ("Open-Meteo (API)", fetch_from_open_meteo),
        ("Sinoptik (Scrape)", fetch_from_sinoptik),
        ("Meteofor (Scrape)", fetch_from_meteofor),
    ]

    for source_name, fetch_func in sources:
        temp = fetch_func()
        if temp is not None:
            return {
                "status": "success",
                "temperature": temp,
                "source": source_name,
                "unit": "°C",
            }

    return {
        "status": "error",
        "message": "Ни один из источников погоды недоступен",
        "temperature": None,
    }


if __name__ == "__main__":
    # Локальная проверка работы
    result = get_outdoor_temperature()
    print("Результат опроса:", result)