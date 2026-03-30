import os
import time
import subprocess
import math
from dronekit import connect, VehicleMode

print("--- U-SPACE TRAFFIC CONTROLLER BOOTING ---")

# 1. Spawn Drones
os.makedirs("drone1_data", exist_ok=True)
os.makedirs("drone2_data", exist_ok=True)

print("Launching Drones in the background...")
d1_process = subprocess.Popen(["py", "-m", "dronekit_sitl", "copter", "--instance", "0", "--home=-35.363261,149.165230,584,0"], cwd="drone1_data")
d2_process = subprocess.Popen(["py", "-m", "dronekit_sitl", "copter", "--instance", "1", "--home=-35.363261,149.165700,584,0"], cwd="drone2_data")

print("Waiting 10 seconds for simulator programs to open...")
time.sleep(10)

# 2. Connect to drones
print("Connecting to telemetry streams...")
drone1 = connect('tcp:127.0.0.1:5760', wait_ready=True)
drone2 = connect('tcp:127.0.0.1:5770', wait_ready=True)

print("\n[SYSTEM] Drones connected.")

# 3. Define our Traffic Control Functions
def get_distance_meters(location1, location2):
    dlat = location2.lat - location1.lat
    dlong = location2.lon - location1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

def arm_and_takeoff(vehicle, target_altitude, drone_name):
    print(f"[{drone_name}] OVERRIDE: Disabling strict hardware checks...")
    vehicle.parameters['ARMING_CHECK'] = 0
    time.sleep(1)
        
    print(f"[{drone_name}] Waiting for 3D GPS Lock...")
    while vehicle.gps_0.fix_type < 3:
        time.sleep(1)
        
    # THE FIX: Don't guess the time. Ask the computer directly and print its status.
    print(f"[{drone_name}] GPS Locked! Waiting for Navigation Computer to confirm ready (is_armable)...")
    while not vehicle.is_armable:
        print(f"   -> {drone_name} Booting internal systems... (Status: {vehicle.system_status.state})")
        time.sleep(2)
        
    print(f"[{drone_name}] Systems Green! Setting GUIDED mode...")
    vehicle.mode = VehicleMode("GUIDED")
    
    while vehicle.mode.name != 'GUIDED':
        print(f"   -> {drone_name} Retrying GUIDED mode switch...")
        vehicle.mode = VehicleMode("GUIDED")
        time.sleep(2)
        
    print(f"[{drone_name}] Mode is GUIDED. Arming motors...")
    vehicle.armed = True
    
    while not vehicle.armed:
        print(f"   -> {drone_name} Retrying Motor Arming...")
        vehicle.armed = True
        time.sleep(2)
        
    print(f"[{drone_name}] Motors armed! Taking off to {target_altitude} meters...")
    vehicle.simple_takeoff(target_altitude)
    
    while True:
        current_alt = vehicle.location.global_relative_frame.alt
        if current_alt >= target_altitude * 0.95:
            print(f"[{drone_name}] Reached target altitude.")
            break
        time.sleep(1)

# 4. Execute the Flight Plan
print("\n[ATC COMMAND] Initiating Takeoff Sequence...")
arm_and_takeoff(drone1, 10, "Drone 1")
arm_and_takeoff(drone2, 10, "Drone 2")

print("\n[ATC STATUS] Both drones airborne.")

# Command Drone 1 to fly towards Drone 2
target_location = drone2.location.global_relative_frame
print("[ATC COMMAND] Drone 1 ordered to fly towards Drone 2's position...")
drone1.simple_goto(target_location)

# 5. THE U-SPACE RADAR LOOP
print("\n--- RADAR ACTIVE: MONITORING AIRSPACE ---")
while True:
    pos1 = drone1.location.global_relative_frame
    pos2 = drone2.location.global_relative_frame
    
    distance = get_distance_meters(pos1, pos2)
    print(f"Radar Ping: Distance is {distance:.2f} meters")
    
    if distance < 15.0:
        print("\n[WARNING] COLLISION RISK DETECTED!")
        print("[ATC OVERRIDE] Forcing Drone 1 to BRAKE immediately.")
        drone1.mode = VehicleMode("BRAKE")
        break 
        
    time.sleep(1)

# 6. Clean up
print("\nWait 5 seconds to observe emergency stop...")
time.sleep(5)
print("Simulation complete. Shutting down...")
drone1.close()
drone2.close()
d1_process.terminate()
d2_process.terminate()
print("Airspace closed.")