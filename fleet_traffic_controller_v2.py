import time
from dronekit import connect

print("--- U-SPACE: AEROGUARD-IQ TELEMETRY RADAR ---")

fleet_ports = [5760, 5770, 5780]
fleet = []

print("[ATC] Initiating connection sequence to all aircraft...")

for i, port in enumerate(fleet_ports):
    v = connect(f'tcp:127.0.0.1:{port}', wait_ready=False, heartbeat_timeout=9999)
    v._heartbeat_timeout = 9999
    v.wait_ready(timeout=9999)
    
    v.parameters['FS_THR_ENABLE'] = 0 
    for ch in range(1, 5):
        v.parameters[f'RC{ch}_MIN'] = 1000
        v.parameters[f'RC{ch}_MAX'] = 2000
        v.parameters[f'RC{ch}_TRIM'] = 1500
        
    print(f"       [SUCCESS] Drone {i+1} connected!")
    fleet.append(v)

print("\n[PRE-FLIGHT] Waiting for GPS & EKF Alignment...")
for i, drone in enumerate(fleet):
    while drone.gps_0.fix_type is None or drone.gps_0.fix_type < 3:
        time.sleep(1)
    while not drone.is_armable:
        time.sleep(2)
    print(f"   -> Drone {i+1} is EKF Aligned and READY.")

print("\n[COMMAND] Arming entire fleet...")
for drone in fleet:
    drone.channels.overrides = {'1': 1500, '2': 1500, '3': 1000, '4': 1500}
time.sleep(2)

for drone in fleet:
    drone.armed = True
    
all_armed = False
while not all_armed:
    all_armed = all(drone.armed for drone in fleet)
    time.sleep(1)

print("!!! PUSHING FLEET THROTTLE TO 80% !!!\n")
for drone in fleet:
    drone.channels.overrides = {'3': 1800}

# --- THE RADAR MATRIX ---
print(f"{'ID':<4} | {'LATITUDE':<12} | {'LONGITUDE':<12} | {'ALT':<7} | {'HDG':<4} | {'SPEED'}")
print("-" * 65)

for step in range(15):
    for i, drone in enumerate(fleet):
        loc = drone.location.global_relative_frame
        lat = f"{loc.lat:.6f}" if loc else "N/A"
        lon = f"{loc.lon:.6f}" if loc else "N/A"
        alt = f"{loc.alt:.2f}m" if loc else "0.00m"
        hdg = f"{drone.heading}°"
        spd = f"{drone.groundspeed:.2f} m/s"
        
        print(f"D{i+1:<2} | {lat:<12} | {lon:<12} | {alt:<7} | {hdg:<4} | {spd}")
    
    print("-" * 65)
    time.sleep(1)

print("\n[MISSION] Cutting fleet throttle to 0% to land...")
for drone in fleet:
    drone.channels.overrides = {'3': 1000}
time.sleep(5)

for drone in fleet:
    drone.armed = False
    drone.close()
    
print("MISSION ENDED.")