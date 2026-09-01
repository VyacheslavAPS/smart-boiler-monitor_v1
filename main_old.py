#MicroPython
import machine
import onewire, ds18x20
import time
import urequests
import ujson
import pcd8544  # Драйвер дисплея должен быть на ESP

# --- НАСТРОЙКИ (КОНФИГУРАЦИЯ) ---
WIFI_SSID = "Your_SSID"
WIFI_PASS = "Your_PASS"
API_URL = "http://192.168.1.100"  # IP твоего FastAPI сервера
TG_TOKEN = "your_bot_token"
TG_CHAT_ID = "your_chat_id"

# --- ЖЕЛЕЗО (PINS) ---
# Датчики температуры (1-Wire)
ds_pin = machine.Pin(4)  # D2
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

# Датчики 220В (Input)
pin_grid = machine.Pin(14, machine.Pin.IN)  # D5
pin_inverter = machine.Pin(12, machine.Pin.IN)  # D6

# Датчик потока (Interrupt)
flow_pin = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)  # D7
pulse_count = 0

# Дисплей Nokia 5110 (SPI)
spi = machine.SPI(1, baudrate=8000000)
lcd = pcd8544.PCD8544(spi, machine.Pin(15), machine.Pin(5), machine.Pin(16))  # CS=D8, DC=D1, RST=D0


# --- ЛОГИКА ---
def count_pulse(pin):
    global pulse_count
    pulse_count += 1


flow_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=count_pulse)


def get_data():
    global pulse_count
    # 1. Опрос температур
    roms = ds_sensor.scan()
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    temps = {str(rom): round(ds_sensor.read_temp(rom), 1) for rom in roms}

    # 2. Состояние питания
    grid = bool(pin_grid.value())
    inv = bool(pin_inverter.value())

    # 3. Анализ потока (сброс счетчика после замера)
    current_pulses = pulse_count
    pulse_count = 0
    pump_ok = current_pulses > 5

    return {
        "temps": temps,
        "power": {"grid": grid, "inv": inv},
        "pump": {"ok": pump_ok, "pulses": current_pulses}
    }


def update_display(data):
    lcd.fill(0)
    lcd.text("MONITOR v1.0", 0, 0, 1)
    # Вывод температур (пример для двух первых)
    t_list = list(data['temps'].values())
    if len(t_list) >= 2:
        lcd.text("In:  {} C".format(t_list[0]), 0, 12, 1)
        lcd.text("Out: {} C".format(t_list[1]), 0, 22, 1)

    p_status = "GRID" if data['power']['grid'] else "BATTERY"
    lcd.text("Pwr: " + p_status, 0, 34, 1)

    pump_txt = "PUMP: OK" if data['pump']['ok'] else "PUMP: ERR!"
    lcd.text(pump_txt, 0, 42, 1)
    lcd.show()


def notify(msg):
    print("Notification:", msg)
    try:
        url = "https://api.telegram.org{}/sendMessage?chat_id={}&text={}".format(TG_TOKEN, TG_CHAT_ID, msg)
        urequests.get(url).close()
    except:
        pass


# --- ГЛАВНЫЙ ЦИКЛ ---
last_grid_state = True

while True:
    try:
        payload = get_data()
        update_display(payload)

        # Логика алертов
        if not payload['power']['grid'] and last_grid_state:
            notify("Внимание! Пропала сеть. Переход на инвертор.")
            last_grid_state = False
        elif payload['power']['grid'] and not last_grid_state:
            notify("Сеть восстановлена.")
            last_grid_state = True

        if payload['power']['inv'] and not payload['pump']['ok']:
            notify("АЛАРМ: Питание есть, потока НЕТ!")

        # Отправка на сервер (опционально)
        # urequests.post(API_URL, json=payload).close()

    except Exception as e:
        print("Loop error:", e)

    time.sleep(10)