# Troubleshooting Archive: The API Bug Logs

This folder contains the historical development scripts and failed execution logs generated during the initial telemetry connection phase of the U-Space Traffic Control project. 

**Note: These scripts are non-functional on Windows environments and are kept strictly for documentation and debugging reference.**

## Why did these fail?
The scripts in this archive (e.g., `auto_mission_failed_code.py`, `manual_connect_failed_code.py`) attempt to use the standard high-level DroneKit API wrappers, specifically `VehicleMode("GUIDED")` and `vehicle.simple_takeoff()`. 

Due to a library routing bug in `pymavlink` on Windows, these string-to-ENUM translations fail silently. The Python script executes without throwing a local error, but the MAVLink transport layer never actually transmits the mode-change packet to the flight controller, causing the drone to remain indefinitely grounded in `STABILIZE` mode or trigger an Auto-Disarm timeout.

## The Resolution
The debugging process documented in these files ultimately led to the creation of the `virtual_pilot.py` script located in the main repository root. 

The successful workaround completely bypasses these high-level wrappers in favor of:
1. Raw MAVLink injection (`_master.set_mode()`).
2. Virtual RC channel overrides to manually arm and push throttle in `STABILIZE` mode.

If you are looking for the working flight controller, please return to the root directory.
