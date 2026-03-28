# Intelligent U-Space Traffic Control 🚁🚦
**Automated Multi-UAV Deconfliction using MAVLink**

## Overview
This project serves as the command-and-control layer for high-density drone operations. While edge intelligence (like **AeroGuard-IQ**) handles individual drone survival, and long-range networks (like **Project Aether-Link**) maintain connectivity, this system acts as the centralized "Digital Air Traffic Controller."

It uses **DroneKit** and **SITL** to simulate multiple UAVs sharing the same airspace, continuously monitoring telemetry to predict and prevent collisions.

## Key Features
* **Multi-Agent Simulation:** Spawns and manages multiple virtual drones simultaneously.
* **Real-Time Telemetry Monitoring:** Continuously parses GPS and altitude data from all active MAVLink streams.
* **Automated Conflict Resolution:** Implements dynamic distance checking. If two drones breach the minimum safety radius (e.g., 5 meters), the system automatically commands the lower-priority UAV to brake or reroute.

## Tech Stack
* **Language:** Python
* **Protocols:** MAVLink
* **Simulation:** DroneKit-SITL, MAVProxy
