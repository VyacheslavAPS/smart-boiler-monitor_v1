# Smart Boiler Monitor & Automation System (v1)

An engineering solution designed to monitor, log, and optimize gas boiler heating cycles based on real-time data analysis and multi-source weather forecasting. Originally conceived for microcontrollers (Raspberry Pi Pico / ESP32 platforms), this software architecture bridges embedded data collection with high-level data processing and analytical reporting.

## Core Architecture & Modules

The system is modularly structured to ensure high reliability, asynchronous data handling, and clean separation of concerns:

*   **`main.py`** — The central runtime orchestrator that coordinates hardware status loops, timing intervals, and peripheral communications.
*   **`server.py`** — Network communication layer designed to accept incoming metrics from edge modules (via wired Ethernet W5500 / wireless shunts) and handle remote control commands.
*   **`weather_service.py`** — An integration client that extracts real-time meteorological data and forecasts from external APIs to implement weather-compensating temperature regulation algorithms.
*   **`analyze_heating.py`** — Analytical backend that processes raw operational logs, computes thermal efficiency, and generates visual charts (`heating_report.png`) using Python's data stack.
*   **`heating_log.csv`** — Time-series storage file tracking structural telemetry, boiler states, and environment temperatures.

## Key Features

*   **Multi-Source Weather Parsing:** Automated API integration to poll local weather conditions for forward-looking system adjustments.
*   **Data Logging & Diagnostics:** Complete local retention of system performance metrics into highly parsable formats.
*   **Visual Reporting:** Programmatic generation of temperature/load charts to visually identify overconsumption and system cycles.
*   **Embedded-to-Cloud Ready:** Built with clear structural boundaries, making it highly portable between Linux environments (Edge devices) and lightweight RTOS microcontrollers.

## Tech Stack

*   **Language:** Python 3.x
*   **Libraries:** Requests, Matplotlib (for visualization), Pandas/CSV modules (data pipelines).
*   **Hardware Compatibility:** Raspberry Pi Pico (MicroPython), ESP32, W5500 Ethernet Modules, Linux Edge Hubs.
