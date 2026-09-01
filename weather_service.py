
# Варианты запроса и получения данных по API для котла с двух погодных серверов
# import requests
#
# # Жестко заданные координаты объекта (не зависят от VPN)
# # Например, для Киевской области: Latitude = 50.45, Longitude = 30.52
# LOCATION_LAT = 50.45
# LOCATION_LON = 30.52
#
#
# def get_from_primary_api(lat: float, lon: float) -> float:
#   """Источник №1: Open-Meteo API."""
#   url = "https://api.open-meteo.com/v1/forecast"
#   params = {
#       "latitude": lat,
#       "longitude": lon,
#       "hourly": "temperature_2m",
#       "forecast_days": 1,
#   }
#   # timeout=3 означает: если сервер не ответил за 3 секунды, бросаем ошибку
#   response = requests.get(url, params=params, timeout=3)
#   response.raise_for_status()  # Проверяем, что код ответа 200 OK
#
#   data = response.json()
#   hourly_temps = data["hourly"]["temperature_2m"]
#
#   # Возвращаем минимальную температуру на следующие 24 часа
#   return min(hourly_temps)
#
#
# def get_from_secondary_api(lat: float, lon: float) -> float:
#   """Источник №2 (Резервный): wttr.in (возвращает JSON по координатам)."""
#   url = f"https://wttr.in/{lat},{lon}"
#   params = {"format": "j1"}  # Просим вернуть данные в формате JSON
#
#   response = requests.get(url, params=params, timeout=3)
#   response.raise_for_status()
#
#   data = response.json()
#   # Извлекаем прогнозируемую минимальную температуру на сегодня
#   min_temp = float(data["weather"][0]["mintempC"])
#   return min_temp
#
#
# def get_reliable_weather_forecast(
#     lat: float = LOCATION_LAT, lon: float = LOCATION_LON
# ) -> dict:
#   """Главная функция: запрашивает основной сервис, при сбое стучит в резервный."""
#   # 1. Пробуем получить данные с основного сервера
#   try:
#     print("Запрос к основному погодному API (Open-Meteo)...")
#     min_temp = get_from_primary_api(lat, lon)
#     return {"status": "ok", "source": "primary", "min_temp_24h": min_temp}
#   except Exception as e:
#     print(f"Основной API недоступен ({e}). Переключаемся на резервный...")
#
#   # 2. Если основной сбойнул — пробуем резервный
#   try:
#     print("Запрос к резервному погодному API (wttr.in)...")
#     min_temp = get_from_secondary_api(lat, lon)
#     return {"status": "ok", "source": "secondary", "min_temp_24h": min_temp}
#   except Exception as e:
#     print(f"Резервный API также недоступен ({e}).")
#
#   # 3. Если ВСЕ сервисы упали — возвращаем аварийный режим
#   return {
#       "status": "fallback",
#       "source": "none",
#       "min_temp_24h": 0.0,  # Безопасная дефолтная оценка
#   }
#
#
# # --- ПРОВЕРКА РАБОТЫ ---
# if __name__ == "__main__":
#   result = get_reliable_weather_forecast()
#   print("Результат работы модуля:", result)
#
#





# # Варианты запроса и получения данных по API url = "https://wttr.in/50.45,30.52?format=j1"
# import requests
#
# def get_time_str(time_val):
#     time_hour = int(time_val)//100
#     return time_hour
#
# # 1. Запрашиваем JSON по вашим координатам
# url = "https://wttr.in/50.45,30.52?format=j1"
# response = requests.get(url, timeout=3)
#
# # 2. Преобразуем ответ из формата JSON в Python dict
# data = response.json()
#
# # 3. Достаем минимальную температуру из первого дня прогноза ('weather'[0])
# min_temp_str = data["weather"][0]["mintempC"]  # Получаем строку "12"
# max_temp_str = data["weather"][0]["maxtempC"] # "maxtempC": "22",
# avg_temp_str = data["weather"][0]["avgtempC"] # "avgtempC": "17",
# # humidity
# # pressure
# # windspeedKmph
# min_temp = float(min_temp_str)  # Переводим в число 12.0
# max_temp = float(max_temp_str)
# avg_temp = float(avg_temp_str)
# print(f"Минимальная температура на сегодня: {min_temp}°C")
# print(f"Максимальная температура на сегодня: {max_temp}°C")
# print(f"Средняя температура на сегодня: {avg_temp}°C")
#
# # Извлекаем список почасовых прогнозов на первый день
# hourly_forecasts = data["weather"][0]["hourly"]
#
# # Проходим циклом по каждому часу
# for item in hourly_forecasts:
#   time_val = item["time"]  # Время (например, "300" = 03:00)
#   temp_val = item["tempC"]  # Температура
#   humidity = item["humidity"]
#   pressure = item["pressure"]
#   windspeedKmph = item["windspeedKmph"]
#   time_new = get_time_str(time_val)
#   print(f"В {time_new}:00 часов будет температура: {temp_val}°C , давление: {pressure}, влажность: {humidity}, скорость ветра: {windspeedKmph}")



# Варианты запроса по API и разбор API
#
# Посмотреть структуру JSON-ответа и узнать доступные поля можно двумя базовыми путями: через документацию API и с помощью инструментов разработчика.
#
# Для примера с [https://api.open-meteo.com/v1/forecast](https://api.open-meteo.com/v1/forecast) разберем оба варианта.
# Вариант 1. Посмотреть в браузере (быстрый практический способ)
#
# Ответ любого открытого API можно увидеть прямо в браузере.
#
#     Сформируйте тестовую ссылку (URL) с минимальными параметрами:
#     [https://api.open-meteo.com/v1/forecast?latitude=50.45&longitude=30.52&hourly=temperature_2m](https://api.open-meteo.com/v1/forecast?latitude=50.45&longitude=30.52&hourly=temperature_2m)
#
#     Вставьте её в адресную строку браузера и нажмите Enter.
#
# Вы увидите «сырой» JSON-текст:
# JSON
# {
#   "latitude": 50.45,
#   "longitude": 30.52,
#   "generationtime_ms": 0.12,
#   "utc_offset_seconds": 0,
#   "timezone": "GMT",
#   "timezone_abbreviation": "GMT",
#   "elevation": 168.0,
#   "hourly_units": {
#     "time": "iso8601",
#     "temperature_2m": "°C"
#   },
#   "hourly": {
#     "time": [
#       "2026-09-01T00:00",
#       "2026-09-01T01:00"
#     ],
#     "temperature_2m": [
#       18.2,
#       17.5
#     ]
#   }
# }
#
# Чтобы структура отображалась красиво с подсветкой и сворачиваемыми блоками, установите
# расширение для браузера (например, JSON Formatter для Chrome/Firefox).
#
# Вариант 2. Сделать принт структуры в Python
#
# Если вы уже пишете код, структуру можно вывести прямо в консоль Python, использую библиотеку
# json для красивого форматирования (pretty print):
#
# Python
# #
# import json
# import requests
#
# url = "https://api.open-meteo.com/v1/forecast"
# params = {
#     "latitude": 50.45,
#     "longitude": 30.52,
#     "hourly": "temperature_2m,relative_humidity_2m",  # Запрашиваем температуру и влажность
# }
#
# response = requests.get(url, params=params)
# data = response.json()
#
# # json.dumps() с параметром indent=4 выводит красивый форматированный текст
# print(json.dumps(data, indent=4))
#
# # Глядя на выведенный текст в консоли, сразу видны имена всех ключей
# (latitude, hourly, temperature_2m) и тип данных (словарь {} или список []).
#
# Вариант 3. Изучить официальную документацию
#
# У Open-Meteo есть интерактивный конструктор на сайте open-meteo.com/en/docs.
#
#     Вы отмечаете галочками нужные параметры (например, Temperature (2 m), Relative Humidity (2 m),
#     Direct Normal Irradiance).
#
#     Сайт снизу сам генерирует готовый URL и показывает пример JSON-ответа со всеми полями и
#     их единицами измерения.
#
# Как «читать» структуру Open-Meteo в Python
#
# Обратите внимание на разницу между wttr.in и open-meteo.com:
#
#     В wttr.in ключ hourly содержит список словарей [{"time": "0", "tempC": "18"}, ...].
#
#     В open-meteo.com ключ hourly содержит словарь параллельных списков:
#
# Python
#
# # Извлечение данных из Open-Meteo
# times = data["hourly"]["time"]  # Список всех меток времени ['2026-09-01T00:00', ...]
# temps = data["hourly"][
#     "temperature_2m"
# ]  # Список всех температур [18.2, 17.5, ...]
#
# # Сопоставление времени и температуры по индексу
# for i in range(len(times)):
#   print(f"В время {times[i]} температура: {temps[i]}°C")
#
# Отличный JSON от Open-Meteo!
# На нем очень удобно разобрать, как извлекать данные, когда вместо
# списка словарей приходят два параллельных списка (массива).
#
# Посмотрим на блок "hourly":
#
#     "time" — список временных меток (всего 168 часов, то есть 7 дней).
#
#     "temperature_2m" — список температур, где элемент с индексом 0 соответствует времени с
#     индексом 0, элемент с индексом 1 — времени с индексом 1 и так далее.
#
# Как вытащить отсюда минимальную температуру и график по часам
#
# Попробуем написать чистый, понятный Python-код, который обрабатывает этот конкретный ответ
# (например, сохраненный в переменную data или загруженный из API).
#
# Python
# Представим, что data — это ваш словарь с JSON-ответом
# # (для примера покажем работу с первыми 24 часами, то есть с сегодняшним днем)
#
# # 1. Забираем списки времени и температур из блока 'hourly'
# times_all = data["hourly"]["time"]
# temps_all = data["hourly"]["temperature_2m"]
#
# # 2. Возьмем данные только на первые 24 часа (срез от 0 до 24)
# today_times = times_all[:24]
# today_temps = temps_all[:24]
#
# # 3. Находим минимальную, максимальную и среднюю температуру за первые сутки
# min_temp = min(today_temps)
# max_temp = max(today_temps)
# avg_temp = round(sum(today_temps) / len(today_temps), 1)
#
# print(f"Минимальная температура на сегодня: {min_temp}°C")
# print(f"Максимальная температура на сегодня: {max_temp}°C")
# print(f"Средняя температура на сегодня: {avg_temp}°C")
# print("-" * 50)
#
#
# # 4. Проходим по часам через встроенную функцию zip()
# # zip() связывает элементы двух списков попарно: (время, температура)
# for time_str, temp in zip(today_times, today_temps):
#   # time_str выглядит как "2026-09-01T03:00"
#   # Отрежем только часы и минуты через split("T")
#   time_only = time_str.split("T")[1]  # Получим "03:00"
#
#   print(f"В {time_only} температура: {temp}°C")
#
# Разбор двух интересных фишек Python в этом коде:
#
#     Срезы [:24]:
#     Так как Open-Meteo прислал прогноз сразу на 7 дней (168 значений), запись temps_all[:24]
#     говорит Python: «возьми первые 24 элемента из списка». Это самый простой способ отсечь
#     лишние дни.
#
#     Функция zip(today_times, today_temps):
#     Вместо того чтобы писать сложный цикл по индексам range(len(...)), функция zip берет два
#     списка и на каждом шаге цикла выдает пару: элемент из первого списка и соответствующий ему
#     элемент из второго.
#
#         1-я итерация: "2026-09-01T00:00" и 21.9
#
#         2-я итерация: "2026-09-01T01:00" и 21.2
#
#         и так далее.
#
#     Строковый метод .split("T")[1]:
#     Строка "2026-09-01T05:00" разбивается буквой "T" на две части: ["2026-09-01", "05:00"]. Взяв
#     элемент с индексом [1], мы сразу получаем красивое время "05:00" без вызова функций
#     форматирования.
#
# Вывод такого скрипта на ваших данных покажет минимальные 16.8°C в районе 23:00 и
# пиковые 27.4°C в 10:00 утра.
#
# Вы абсолютно правы: индекс массива от 0 до 167 (всего 168 элементов) — это просто порядковый
# номер часа в полученном ответе, начиная с того момента, который вернул сервер.
#
# Так как Open-Meteo отдает данные подряд, час за часом, индексы распределяются так:
#
#     Индикация первых суток (сегодня): индексы от 0 до 23 (первые 24 элемента).
#
#     Индикация вторых суток (завтра): индексы от 24 до 47.
#
#     Третий день: от 48 до 71, и так далее.
#
# И да, если вам нужен прогноз на конкретную дату или конкретный промежуток времени, у вас есть
# два пути.
#
# Путь 1. Простой: Мы сами берем нужные интервалы (срезы) в коде
#
# Если вам нужен прогноз, например, строго на сегодня и строго на завтра, вы можете взять готовые
# срезы списков без сложных вычислений:
#
# Python
#
# # Сегодня (первые 24 часа)
# today_temps = temps_all[0:24]
# min_today = min(today_temps)
#
# # Завтра (следующие 24 часа)
# tomorrow_temps = temps_all[24:48]
# min_tomorrow = min(tomorrow_temps)
#
# print(f"Минимум на сегодня: {min_today}°C")
# print(f"Минимум на завтра: {min_tomorrow}°C")
#
# Но что делать, если вы делаете запрос посреди дня (например, в 14:00), или если вам нужно найти
# данные за конкретную дату, независимо от того, с какого часа сервер начал список?

# Путь 2. Точный: Парсинг даты с помощью модуля datetime
#
# В профессиональном коде для сбора данных (Data Engineering) не рассчитывают индексы «на глаз»,
# а связывают каждый элемент времени с объектом даты Python.
#
# Мы можем легко сгруппировать данные по датам (YYYY-MM-DD):
#
# Python
# from datetime import datetime
#
# # Создаем словарь для группировки температур по дням
# # Ключ — дата "2026-09-01", Значение — список температур за этот день
# daily_data = {}
#
# for time_str, temp in zip(times_all, temps_all):
#   # Преобразуем строку вида "2026-09-01T14:00" в объект даты
#   dt = datetime.fromisoformat(time_str)
#   date_key = dt.strftime("%Y-%m-%d")  # Получаем чистую дату "2026-09-01"
#
#   # Добавляем температуру в список соответствующего дня
#   if date_key not in daily_data:
#     daily_data[date_key] = []
#   daily_data[date_key].append(temp)
#
# # Теперь у нас есть удобный словарь по дням!
# for date, temps in daily_data.items():
#   print(
#       f"Дата {date}: мин = {min(temps)}°C, макс = {max(temps)}°C, средняя = {round(sum(temps)/len(temps), 1)}°C"
#   )
#
# Путь 3. Самый ленивый и правильный: Попросить сам Open-Meteo ограничить выборку!
#
# Вам даже не обязательно скачивать все 168 часов и высчитывать индексы вручную. Вы можете передать
# параметры прямо в URL запроса, чтобы API отдал только то, что вам нужно.
#
# Если вам нужны данные строго на 1 день (или за конкретные даты), в запрос добавляются параметры
# forecast_days или start_date / end_date:
#
# Python
#
# params = {
#     "latitude": 50.45,
#     "longitude": 30.52,
#     "hourly": "temperature_2m",
#     "forecast_days": 1,  # Просим вернуть ВСЕГО 24 часа (1 день)!
# }
#
#
# В этом случае список hourly вернет ровно 24 элемента (с индексами от 0 до 23), и вам не придется
# ничего высчитывать.
#
#
#
# Здесь мы как раз возвращаемся к тому моменту, который обсуждали чуть выше: разнице между
# открытыми API и обычными сайтами погоды.
#
# Запрос [https://meteofor.com.ua/v1/forecast](https://meteofor.com.ua/v1/forecast), который вы
# написали — не сработает, и вот почему:
#
#     meteofor.com.ua (бывший Gismeteo в Украине) — это веб-сайт для людей, а не сервисная система
#     для программ.
#
#     У них нет официального публичного адреса /v1/forecast, принимающего параметры latitude и
#     longitude.
#
#     Если вы отправка сделаете этот запрос через requests.get(), сервер вернет
#     ошибку 404 Not Found (Страница не найдена) или HTML-страницу с ошибкой,
#     и вызов .json() упадет с исключением.
#
# Как на самом деле работает сбор данных (Scraping) с meteofor.com.ua
#
# Если стояла бы задача забрать погоду именно с Meteofor (например, для Фастова или Киева),
# сценарий работы будет совсем другим — это чистый Web Scraping (разбор HTML):
#
#     Адрес (URL) будет ссылкой на обычную страницу:
#     [https://meteofor.com.ua/weather-fastiv-4957/](https://meteofor.com.ua/weather-fastiv-4957/)
#     (или для Киева .../weather-kyiv-4944/).
#
#     Ответом сервера будет не JSON, а обычный HTML-код страницы (тот же самый код, который
#     браузер превращает в картинки и таблицы).
#
#     Для извлечения данных используется библиотека BeautifulSoup (или lxml), которая ищет
#     нужные теги в структуре документа.
#
# Пример рабочего кода для парсинга HTML с Meteofor
#
# Для работы этого подхода нужны библиотеки requests и beautifulsoup4:
#
# Bash
#
# pip install requests beautifulsoup4
#
# Вот как выглядит парсер HTML-страницы Meteofor:
#
# Python
#
# import requests
# from bs4 import BeautifulSoup
#
# # Ваш точный URL для Фастова
# url = "https://meteofor.com.ua/ru/weather-fastiv-12087/"
#
# headers = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
#         " like Gecko) Chrome/120.0.0.0 Safari/537.36"
#     )
# }
#
# try:
#   response = requests.get(url, headers=headers, timeout=5)
#   response.raise_for_status()
#
#   soup = BeautifulSoup(response.text, "html.parser")
#
#   # 1. Находим первый тег <temperature-value> на странице (это текущая температура)
#   temp_tag = soup.find("temperature-value")
#
#   if temp_tag:
#     # 2. Пробуем забрать значение из атрибута value="..."
#     # В BeautifulSoup атрибуты тега достаются как элементы словаря: tag['attribute']
#     if "value" in temp_tag.attrs:
#       temp_value = temp_tag["value"]
#       print(
#           f"Текущая температура в Фастове (из атрибута value): {temp_value}°C"
#       )
#     else:
#       # Если атрибута нет, забираем обычный текст внутри тега
#       print(f"Текущая температура (из текста): {temp_tag.text.strip()}°C")
#   else:
#     print("Элемент с температурой не найден.")
#
# except Exception as e:
#   print(f"Ошибка при скачивании страницы: {e}")
#
#
# # Совершенно верно! Вы нашли актуальный URL для Фастова на русскоязычной версии сайта
# (/ru/weather-fastiv-12087/).
#
# Давайте запустим скрипт с этим адресом. Но тут есть один очень важный практический нюанс
# Web Scraping, с которым сталкиваются все разработчики.
#
# Когда вы откроете эту страницу в браузере и нажмете F12, вы увидите, что температура лежит
# внутри тега <temperature-value>:
#
# HTML
#
# <temperature-value value="+22"></temperature-value>
#
# Многие современные сайты (включая Meteofor) рендерят цифры с помощью JavaScript прямо в
# браузере пользователя, а сам текст внутри тега может быть пустым при базовом скачивании
# через requests. Но значение температуры при этом записано в атрибут value этого тега!
# скрипт уже написан с учетом "забрать из value"
#
# Чему учит этот пример (Ключевой урок по BeautifulSoup)
#
# В HTML тег выглядит так:
# <temperature-value class="unit_temperature" value="+22">+22</temperature-value>
#
# В BeautifulSoup у нас есть два способа забрать данные из тега:
#
#     temp_tag.text — забирает текст между открывающим и закрывающим тегом
#     (то, что видит человек на экране).
#
#     temp_tag['value'] или temp_tag['class'] — забирает значение конкретного атрибута внутри
#     самого тега (то, что использует фронтенд-скрипт).
#
# При парсинге реальных сайтов атрибуты (data-price, value, href, src) часто оказываются гораздо
# надежнее, чем обычный текст!
#
# Вы только что самостоятельно прошли весь базовый путь веб-скрейпинга (Web Scraping):
#
#     Нашли правильный веб-адрес (URL) страницы.
#
#     Сформировали HTTP-запрос с заголовком User-Agent, чтобы сайт не заблокировал
#     автоматический скрипт.
#
#     Загрузили сырой HTML-код страницы через requests.
#
#     Проанализировали структуру HTML через BeautifulSoup.
#
#     Нашли нужный тег (<temperature-value>) и прочитали данные из его атрибута (value).
#
# Главный вывод и сравнение двух подходов
#
# Теперь на практике видна принципиальная разница между двумя способами получения данных:
#
#                   ┌──►    1. Публичный API (Open-Meteo, wttr.in)
#                   │        • Формат: JSON (готовые словари/списки)
#                   │        • Надежность: Высокая (интерфейс не меняется)
#                   │        • Парсинг: Достаем по ключам ['hourly']['temperature_2m']
# Обучение / Проект ┤
#                   │
#                   └──►    2. HTML Scraping (Meteofor, Rozetka, OLX)
#                            • Формат: HTML-разметка страницы
#                            • Надежность: Средняя (верстка сайта может измениться)
#                            • Парсинг: Поиск тегов и атрибутов через BeautifulSoup
#
# Для регулярного автоматического управления котлом в фоновом режиме лучше использовать
# API (Open-Meteo + wttr.in как резерв), так как он работает быстрее, тратит меньше трафика
# и не сломается, если Meteofor решит обновить дизайн сайта.
#
# А полученный опыт парсинга HTML через BeautifulSoup — это как раз тот самый базовый навык,
# # который требуют на позицию Junior Web Scraper / Python Developer.
#
# import scrapy
#
#
# class MeteoforSpider(scrapy.Spider):
#   # 1. Уникальное имя паука для запуска через консоль
#   name = "meteofor"
#
#   # 2. Настройки для этого конкретного паука (headers, задержки и т.д.)
#   custom_settings = {
#       "USER_AGENT": (
#           "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
#       )
#   }
#
#   # 3. Начальные ссылки для скачивания
#   start_urls = ["https://meteofor.com.ua/ru/weather-fastiv-12087/"]
#
#   # 4. Метод parse вызывается автоматически, когда страница скачана
#   def parse(self, response):
#     # Scrapy использует CSS-селекторы или XPath прямо внутри response
#     # (BeautifulSoup внутри Scrapy вообще не нужен!)
#     temp = response.css("temperature-value::attr(value)").get()
#
#     # Вместо print() Scrapy использует yield (генератор) для возврата данных
#     yield {"city": "Fastiv", "temperature": temp}
#
# Как это выглядит для Sinoptik.ua
#
# Если посмотреть верстку сайта Sinoptik, текущая температура там находится в блоке с классом
# today-temp.
#
# Вот как будет выглядеть рабочий паук Scrapy для Sinoptik:
#
# Python
import scrapy
from scrapy.crawler import CrawlerProcess


class SinoptikSpider(scrapy.Spider):
  name = "sinoptik"
  # 1. Подставляем URL Sinoptik
  start_urls = ["https://sinoptik.ua/ru/pohoda/fastiv"]

  custom_settings = {
      "USER_AGENT": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  def parse(self, response):
    # 2. Меняем CSS-селектор под верстку Sinoptik!
    # Ищем элемент с классом today-temp и забираем его текст (::text)
    temp = (
            response.css(".R1ENpvZz::text").get()
            or response.css(".pohoda-now .temp::text").get()
            or response.css("p.today-temp::text").get()
            or response.xpath("//p[contains(text(), '°C')]/text()").get()
    )

    if temp:
      print(f"\n>>> ТЕМПЕРАТУРА НА SINOPTIK (Фастов): {temp.strip()} <<<\n")
    else:
      print("\n>>> Не удалось найти температуру на странице <<<\n")


if __name__ == "__main__":
  process = CrawlerProcess()
  process.crawl(SinoptikSpider)
  process.start()

# Чтобы быстро найти нужный элемент в DevTools (F12) без ручного прокручивания тысяч
# строк HTML-кода:
#
#     Нажмите сочетание клавиш Ctrl + Shift + C (или кликните на значок стрелочки в самом верхнем
#     левом углу панели DevTools).
#
#     Наведите курсор мыши прямо на большую цифру температуры на самой веб-странице и
#     кликните по ней.
#
#     DevTools автоматически подсветит в дереве HTML именно ту строчку, где лежит эта цифра.
#
# Как устроен HTML на Sinoptik.ua
#
# Если кликнуть по текущей температуре, вы увидите примерно такую структуру:
#
# HTML
#
# <p class="today-temp">+18°C</p>
#
# Или блок с подробной погодой на сегодня:
# HTML
#
# <div class="img weatherIcoL">
#     <p class="today-temp">+18°C</p>
# </div>
#
# Какое правило (CSS-селектор) прописать в Scrapy?
#
# В HTML класс элемента обозначается как class="today-temp". В CSS-селекторах точка .
# обозначает поиск по классу:
#
# Python
#
# # Находим тег с классом today-temp и забираем его текст (::text)
# temp = response.css(".today-temp::text").get()
#
# Если нужно забрать значение из таблицы прогноза по часам (например, на 12:00 или 15:00),
# там используются классы видов td.p1, td.p2 и так далее.
#
#  <p class="R1ENpvZz">+21°C</p>
#
# Вот она — точная строчка из HTML!
#
# Класс элемента на Sinoptik сейчас называется R1ENpvZz.
#
# Обратите внимание: такие названия классов (случайные буквы вроде R1ENpvZz) генерируются
# автоматически при сборке сайта. Они могут периодически меняться при обновлениях сайта,
# но прямо сейчас это именно то, что нужно.
# Как теперь прописать селектор в Scrapy
#
# В CSS-селекторах класс обозначается через точку:
#
# Python
#
# def parse(self, response):
#   # Ищем текст внутри элемента с классом R1ENpvZz
#   temp = response.css(".R1ENpvZz::text").get()
#
#   if temp:
#     print(f"\n>>> ТЕМПЕРАТУРА НА SINOPTIK: {temp.strip()} <<<\n")
#   else:
#     print("\n>>> Не удалось найти температуру на странице <<<\n")
#
# Альтернативный вариант (для надежности)
#
# Если динамический класс R1ENpvZz изменится, можно также зацепиться за сам тег <p> внутри
# блока или использовать XPath поиск по содержимому градуса:
# Python
#
# # Вариант через XPath: ищет любой тег <p>, текст которого содержит знак °C
# temp = response.xpath("//p[contains(text(), '°C')]/text()").get()
#
# Запустите скрипт с .R1ENpvZz::text — теперь Scrapy вытащит значение без ошибок!






