# Intelligent U-Space Traffic Control: Low-Level MAVLink Flight Controller Bypass

This repository contains the foundational SITL (Software In The Loop) communication layer for the **Intelligent U-Space Traffic Control** project. 

During the initial development and simulation phase, a critical API routing bug was identified in the standard DroneKit-Python library on Windows, which silently dropped high-level autonomous navigation commands. This script serves as a robust, low-level workaround using direct MAVLink channel injections to establish reliable flight control and telemetry streaming.

## The Engineering Problem
When attempting to transition the ArduPilot SITL (Copter 3.3) into `GUIDED` mode via the standard `VehicleMode("GUIDED")` API wrapper, the command is silently rejected. Diagnostic wiretapping of the `STATUSTEXT` MAVLink packets revealed no internal EKF or pre-arm failures. 

The root cause is a `pymavlink` library mismatch on Windows that fails to translate the string "GUIDED" into the correct MAVLink ENUM machine code, causing the flight controller to ignore the navigation request while remaining in `STABILIZE` mode.

## The Solution: Raw Channel Injection
Rather than relying on the broken high-level API for automated takeoff, `virtual_pilot.py` completely bypasses the autonomous mode wrappers. The script operates by:
1. Connecting to the SITL telemetry stream with an extended patience timeout (bypassing barometer calibration lag).
2. Forcing the EKF (Extended Kalman Filter) to authentically align by allowing standard hardware checks to run their course.
3. Injecting factory RC calibration data directly into the drone's EEPROM to clear failsafes.
4. **Hot-wiring the virtual RC channels (`v.channels.overrides`)** to arm the motors in manual `STABILIZE` mode and physically inject an 80% throttle command to achieve lift.

This ensures a stable, verified connection to the flight controller, allowing the broader U-Space Traffic Control algorithms to be built on top of a reliable transport layer.

## Prerequisites & Installation

Ensure you have Python installed, then install the required MAVLink and DroneKit libraries:

```bash
pip install -r requirements.txt

Author
Pradhyumna Avinash Ramgirwar
M.Sc. Electrical Engineering and Information Technology (EEIT)
Otto von Guericke University (OVGU) - Magdeburg
