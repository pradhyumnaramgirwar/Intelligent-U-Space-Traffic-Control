import time
from dronekit import connect

print("--- U-SPACE: CLEAN FLEET TRAFFIC CONTROLLER ---")

fleet_ports = [5760, 5770, 5780]
fleet = []

print("[ATC] Initiating connection sequence to all aircraft...")

for i, port in enumerate(fleet_ports):
    print(f"\n[LINK] Tower calling Drone {i+1} on Port {port}...")
    
    v = connect(f'tcp:127.0.0.1:{port}', wait_ready=False, heartbeat_timeout=9999)
    v._heartbeat_timeout = 9999
    v.wait_ready(timeout=9999)
    
    # Standard RC Calibration only
    v.parameters['FS_THR_ENABLE'] = 0 
    for ch in range(1, 5):
        v.parameters[f'RC{ch}_MIN'] = 1000
        v.parameters[f'RC{ch}_MAX'] = 2000
        v.parameters[f'RC{ch}_TRIM'] = 1500
        
    print(f"       [SUCCESS] Drone {i+1} brain mapped!")
    fleet.append(v)

print("\n[PRE-FLIGHT] Waiting for GPS & EKF Alignment across the fleet...")
for i, drone in enumerate(fleet):
    while drone.gps_0.fix_type is None or drone.gps_0.fix_type < 3:
        time.sleep(1)
    while not drone.is_armable:
        time.sleep(2)
    print(f"   -> Drone {i+1} is EKF Aligned and READY.")

print("\n--------------------------------------------------")
print("   ALL DRONES READY. INITIATING FLEET TAKEOFF")
print("--------------------------------------------------")

print("[COMMAND] Grabbing Virtual Joysticks for all drones...")
for drone in fleet:
    drone.channels.overrides = {'1': 1500, '2': 1500, '3': 1000, '4': 1500}
time.sleep(2)

print("\n[COMMAND] Arming entire fleet...")
for drone in fleet:
    drone.armed = True
    
# Wait until the flight controller confirms every single drone is armed
all_armed = False
while not all_armed:
    all_armed = all(drone.armed for drone in fleet)
    time.sleep(1)
print("   -> FLEET IS ARMED AND MOTORS ARE SPINNING!")

print("\n!!! PUSHING FLEET THROTTLE TO 80% !!!")
for drone in fleet:
    drone.channels.overrides = {'3': 1800}

# Monitor altitudes for the whole squadron at once
for step in range(15):
    alts = []
    for drone in fleet:
        if drone.location.global_relative_frame:
            alts.append(f"{drone.location.global_relative_frame.alt:.2f}m")
        else:
            alts.append("0.00m")
            
    print(f"   -> Squadron Altitudes: D1 [{alts[0]}] | D2 [{alts[1]}] | D3 [{alts[2]}]")
    time.sleep(1)

print("\n[MISSION] Cutting fleet throttle to 0% to land...")
for drone in fleet:
    drone.channels.overrides = {'3': 1000}
time.sleep(5)

print("[MISSION] Disarming fleet...")
for drone in fleet:
    drone.armed = False

print("\n[SYSTEM] ATC closing connections.")
for drone in fleet:
    drone.close()
    
print("MISSION ENDED.")