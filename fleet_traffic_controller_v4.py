import time
import math # <-- Needed for our Black Box math
from dronekit import connect

print("--- U-SPACE: AEROGUARD-IQ FULL SYSTEM ONLINE ---")

# ==========================================
# THE "BLACK BOX" MATH FUNCTION
# (You don't have to touch this! It just calculates meters between GPS points)
# ==========================================
def get_distance_meters(lat1, lon1, lat2, lon2):
    R = 6378137.0 # Radius of Earth in meters
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
# ==========================================

fleet_ports = [5760, 5770, 5780]
fleet = []

# --- STATIC AVOIDANCE: The Geofence Boundaries ---
SAFE_LAT_MIN = -35.363300
SAFE_LAT_MAX = -35.363255
SAFE_LON_MIN = 149.165100
SAFE_LON_MAX = 149.165500

# --- DYNAMIC AVOIDANCE: The Crash Radius ---
MIN_SAFE_DISTANCE = 15.0 # If they get closer than 5 meters, trigger alarm!

breached_drones = set() 

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
    
while not all(drone.armed for drone in fleet):
    time.sleep(1)

print("!!! PUSHING FLEET THROTTLE TO 80% !!!\n")
for drone in fleet:
    drone.channels.overrides = {'3': 1800}

print(f"{'ID':<4} | {'LATITUDE':<12} | {'LONGITUDE':<12} | {'ALT':<7} | {'STATUS'}")
print("-" * 65)

# Radar Loop
for step in range(20):
    # We need to store the current coordinates to check distances
    current_lats = []
    current_lons = []

    for i, drone in enumerate(fleet):
        loc = drone.location.global_relative_frame
        lat_val = loc.lat if loc else 0.0
        lon_val = loc.lon if loc else 0.0
        alt = f"{loc.alt:.2f}m" if loc else "0.00m"
        
        current_lats.append(lat_val)
        current_lons.append(lon_val)
        status = "SAFE"
        
        # --- LAYER 1: THE STATIC GEOFENCE ---
        if i not in breached_drones:
            if (lat_val < SAFE_LAT_MIN or lat_val > SAFE_LAT_MAX or 
                lon_val < SAFE_LON_MIN or lon_val > SAFE_LON_MAX):
                print(f"\n[ALARM] DRONE {i+1} BREACHED GEOFENCE BOUNDARY! Cutting throttle.")
                drone.channels.overrides = {'3': 1000} 
                breached_drones.add(i)
                
        if i in breached_drones:
            status = "VIOLATION (DESCENDING)"
            
        print(f"D{i+1:<2} | {lat_val:<12.6f} | {lon_val:<12.6f} | {alt:<7} | {status}")
    
    # --- LAYER 2: THE DYNAMIC PROXIMITY ALARM ---
    # Check the distance between Drone 1 & 2, 2 & 3, and 1 & 3
    for j in range(len(fleet)):
        for k in range(j + 1, len(fleet)):
            # Only check drones that are still actively flying (not breached)
            if j not in breached_drones and k not in breached_drones:
                dist = get_distance_meters(current_lats[j], current_lons[j], current_lats[k], current_lons[k])
                
                if dist < MIN_SAFE_DISTANCE:
                    print(f"\n⚠️ [COLLISION WARNING] Drone {j+1} & Drone {k+1} are too close! ({dist:.2f}m apart)")

    print("-" * 65)
    time.sleep(1)

print("\n[MISSION] Mission complete. Cutting remaining fleet throttle to 0%...")
for drone in fleet:
    drone.channels.overrides = {'3': 1000}
time.sleep(5)

for drone in fleet:
    drone.armed = False
    drone.close()
    
print("MISSION ENDED.")