import machine
import onewire, ds18x20
import uasyncio as asyncio
import urequests
import ujson
import network
import time

# ==============================================================================
# 1. КОНФИГУРАЦИЯ И НАСТРОЙКИ
# ==============================================================================
WIFI_SSID = "Your_SSID"
WIFI_PASS = "Your_PASS"
API_URL = "http://192.168.1.100"  # IP вашего FastAPI сервера

TG_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Токен бота Telegram
TG_CHAT_ID = "YOUR_CHAT_ID_HERE"  # Chat ID

CONFIG_FILE = "ds_config.json"

# --- НАЗНАЧЕНИЕ ПИНОВ (ESP32-S3) ---
ds_pin = machine.Pin(4)
pin_grid = machine.Pin(14, machine.Pin.IN)
pin_inverter = machine.Pin(12, machine.Pin.IN)
flow_pin = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)

# Исполнительные реле (1 - ВКЛ, 0 - ВЫКЛ)
relay_bellow = machine.Pin(10, machine.Pin.OUT, value=0)  # Спираль сильфона Eurosit
relay_s1 = machine.Pin(11, machine.Pin.OUT, value=0)  # Скорость насоса 1
relay_s2 = machine.Pin(15, machine.Pin.OUT, value=0)  # Скорость насоса 2
relay_s3 = machine.Pin(16, machine.Pin.OUT, value=0)  # Скорость насоса 3

# --- ИНИЦИАЛИЗА 1-WIRE ---
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

# --- ГЛОБАЛЬНОЕ СОСТОЯНИЕ СИСТЕМЫ ---
system_data = {
    "temps": {},
    "grid_ok": True,
    "pump_ok": True,
    "pump_pulses": 0
}

pulse_count = 0


def count_pulse(pin):
    global pulse_count
    pulse_count += 1


flow_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=count_pulse)


# ==============================================================================
# 2. ПОДКЛЮЧЕНИЕ К WI-FI
# ==============================================================================
async def connect_wifi():
    """Подключение к Wi-Fi сети при старте и контроль связи"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print(f"[Wi-Fi] Подключение к {WIFI_SSID}...")
        wlan.connect(WIFI_SSID, WIFI_PASS)

        # Ждем подключения до 10 секунд (без полной блокировки)
        for _ in range(20):
            if wlan.isconnected():
                break
            await asyncio.sleep_ms(500)

    if wlan.isconnected():
        print("[Wi-Fi] Успешно подключено! IP:", wlan.ifconfig()[0])
    else:
        print("[Wi-Fi Error] Не удалось подключиться к роутеру.")


async def wifi_keepalive_loop():
    """Фоновая задача контроля и автореконнекта Wi-Fi"""
    wlan = network.WLAN(network.STA_IF)
    while True:
        if not wlan.isconnected():
            print("[Wi-Fi] Связь потеряна. Переподключение...")
            wlan.connect(WIFI_SSID, WIFI_PASS)
        await asyncio.sleep(15)  # Проверка каждые 15 секунд


# ==============================================================================
# 3. ИНИЦИАЛИЗАЦИЯ И НАСТРОЙКА ДАТЧИКОВ DS18B20 (10 БИТ + JSON)
# ==============================================================================
def configure_ds18b20_10bit(roms):
    """Установка 10-битного разрешения (время конвертации 187.5 мс)"""
    for rom in roms:
        ds_sensor.write_scratchpad(rom, b'\x00\x00\x3F')


def init_temperature_sensors():
    """Сканирование шины, конфигурирование и привязка датчиков к именам"""
    roms = ds_sensor.scan()
    print(f"[1-Wire] Найдено датчиков: {len(roms)}")

    configure_ds18b20_10bit(roms)
    found_devices = [rom.hex() for rom in roms]
    config = {}

    try:
        with open(CONFIG_FILE, "r") as f:
            config = ujson.load(f)
            print("[Config] Конфигурация датчиков загружена из", CONFIG_FILE)
    except Exception:
        print("[Config] Файл конфигурации не найден. Создаем новый...")

    updated = False
    for dev_hex in found_devices:
        if dev_hex not in config.values():
            updated = True

    if updated or not config:
        config = {
            "boiler_out": found_devices[0] if len(found_devices) > 0 else "",
            "boiler_in": found_devices[1] if len(found_devices) > 1 else "",
            "room_1": found_devices[2] if len(found_devices) > 2 else "",
            "kitchen": found_devices[3] if len(found_devices) > 3 else "",
            "outdoor": found_devices[4] if len(found_devices) > 4 else ""
        }
        with open(CONFIG_FILE, "w") as f:
            ujson.dump(config, f)
        print("[Config] Конфигурация обновлена и сохранена.")

    return config


# ==============================================================================
# 4. АСИНХРОННЫЕ ЗАДАЧИ (TASKS)
# ==============================================================================

async def handle_notification(msg):
    """Отправка уведомлений в Telegram (timeout 3 сек)"""
    print("[Telegram]:", msg)
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={TG_CHAT_ID}&text={msg}"
    try:
        res = urequests.get(url, timeout=3.0)
        res.close()
    except Exception as e:
        print("[Telegram Error]:", e)


async def send_telemetry_to_fastapi():
    """Фоновая отправка телеметрии на FastAPI сервер каждые 5 секунд"""
    while True:
        try:
            # Отправка актуальных данных системы на сервер
            res = urequests.post(
                f"{API_URL}/api/telemetry",
                json=system_data,
                timeout=2.0
            )
            res.close()
        except Exception as e:
            # Не спамим в консоль при мелких сбоях сети
            pass
        await asyncio.sleep(5)


async def change_pump_speed(target_speed):
    """Безопасное переключение обмоток насоса"""
    relay_s1.value(0)
    relay_s2.value(0)
    relay_s3.value(0)
    await asyncio.sleep_ms(100)

    if target_speed == 1:
        relay_s1.value(1)
    elif target_speed == 2:
        relay_s2.value(1)
    elif target_speed == 3:
        relay_s3.value(1)


async def sensors_loop(sensor_map):
    """Задача 1: Опрос датчиков температуры (10 бит) и датчика протока"""
    global pulse_count
    roms_bytes = {name: bytes.fromhex(hex_str) for name, hex_str in sensor_map.items() if hex_str}

    while True:
        try:
            ds_sensor.convert_temp()
            await asyncio.sleep_ms(200)

            temps = {}
            for name, rom in roms_bytes.items():
                temps[name] = round(ds_sensor.read_temp(rom), 1)

            system_data["temps"] = temps

            system_data["pump_pulses"] = pulse_count
            pulse_count = 0
            system_data["pump_ok"] = system_data["pump_pulses"] > 5

        except Exception as e:
            print("[Sensors Loop Error]:", e)

        await asyncio.sleep(2)


async def safety_and_control_loop():
    """Задача 2: Контроль безопасности котла и реле (5 раз/сек)"""
    last_grid_state = True

    while True:
        grid_now = bool(pin_grid.value())
        system_data["grid_ok"] = grid_now

        # 1. АВАРИЯ 220В
        if not grid_now:
            relay_bellow.value(1)  # Греем сильфон, тушим газ
            if last_grid_state:
                asyncio.create_task(handle_notification("КРИТ: Пропала сеть 220В! Котел аварийно заглушен спиралью."))
                last_grid_state = False
        else:
            if not last_grid_state:
                asyncio.create_task(handle_notification("Сеть 220В восстановлена. Переход в штатный режим."))
                last_grid_state = True
            relay_bellow.value(0)

        # 2. Логика насоса
        if grid_now:
            t_in = system_data["temps"].get("boiler_in")

            if not system_data["pump_ok"]:
                relay_bellow.value(1)
                asyncio.create_task(handle_notification("АЛАРМ: Нет протока воды! Котел остановлен."))
            elif t_in is not None:
                if t_in < 40.0:
                    await change_pump_speed(3)
                elif 40.0 <= t_in < 52.0:
                    await change_pump_speed(2)
                elif t_in >= 52.0:
                    await change_pump_speed(1)

        await asyncio.sleep_ms(200)


async def display_loop():
    """Задача 3: Обновление экрана"""
    while True:
        # update_display(system_data)
        await asyncio.sleep(2)


# ==============================================================================
# 5. ТОЧКА ВХОДА (MAIN)
# ==============================================================================
async def main():
    # 1. Подключаемся к Wi-Fi при старте
    await connect_wifi()

    # 2. Инициализируем DS18B20
    sensor_map = init_temperature_sensors()

    print("[System] Запуск асинхронных задач...")
    # 3. Запускаем все параллельные процессы
    await asyncio.gather(
        wifi_keepalive_loop(),
        sensors_loop(sensor_map),
        safety_and_control_loop(),
        send_telemetry_to_fastapi(),
        display_loop()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[System] Программа остановлена вручную")