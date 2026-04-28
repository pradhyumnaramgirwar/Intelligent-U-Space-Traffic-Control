import time
import math
import pickle
import warnings
from dronekit import connect

warnings.filterwarnings("ignore")

print("--- U-SPACE: AEROGUARD-IQ PREDICTIVE AI ONLINE ---")

# --- 1. LOAD THE AI BRAIN ---
try:
    with open('uspace_brain.pkl', 'rb') as f:
        ai_brain = pickle.load(f)
    print("[SYSTEM] Machine Learning Model successfully loaded.")
except:
    print("[ERROR] Could not find aeroguard_brain.pkl! Run train_ai.py first.")
    exit()

def get_distance_meters(lat1, lon1, lat2, lon2):
    R = 6378137.0 
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

fleet_ports = [5760, 5770, 5780]
fleet = []

# --- AIRSPACE PARAMETERS ---
SAFE_LAT_MIN = -35.363300
SAFE_LAT_MAX = -35.363255 # Strict geofence for testing
SAFE_LON_MIN = 149.165100
SAFE_LON_MAX = 149.165500
MIN_SAFE_DISTANCE = 15.0  # Strict collision limit for testing

# HOME coordinates to calculate how far the drone has flown away
HOME_LAT = -35.363261
HOME_LON = 149.165230

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

print(f"{'ID':<3} | {'ALT':<6} | {'GEOFENCE':<10} | {'PREDICTED SNR':<15} | {'AI ACTION'}")
print("-" * 75)

for step in range(20):
    current_lats = []
    current_lons = []

    for i, drone in enumerate(fleet):
        loc = drone.location.global_relative_frame
        lat_val = loc.lat if loc else 0.0
        lon_val = loc.lon if loc else 0.0
        alt_val = loc.alt if loc else 0.0
        
        current_lats.append(lat_val)
        current_lons.append(lon_val)
        
        # 1. Calculate physical metrics
        distance_from_home = get_distance_meters(HOME_LAT, HOME_LON, lat_val, lon_val)
        interference_level = 2 # Let's simulate flying over a highly urban city (Level 2)
        
        # 2. THE MACHINE LEARNING PREDICTION
        # We ask the Random Forest to predict the SNR based on our current altitude and distance
        predicted_snr = ai_brain.predict([[distance_from_home, alt_val, interference_level]])[0]
        
        # 3. Assess the Status
        geo_status = "SAFE"
        ai_action = "FLYING"
        
        if i not in breached_drones:
            # Check AI Signal Prediction First (If SNR is below 45dB, it is critically bad)
            if predicted_snr < 45.0:
                print(f"\n[AI PREDICTION] Drone {i+1} SNR dropping to {predicted_snr:.1f}dB! Executing Signal Loss Override.")
                drone.channels.overrides = {'3': 1000}
                breached_drones.add(i)
                ai_action = "SIGNAL OVERRIDE"
                
            # Then Check Geofence
            elif (lat_val < SAFE_LAT_MIN or lat_val > SAFE_LAT_MAX or 
                lon_val < SAFE_LON_MIN or lon_val > SAFE_LON_MAX):
                print(f"\n[ALARM] DRONE {i+1} BREACHED GEOFENCE!")
                drone.channels.overrides = {'3': 1000} 
                breached_drones.add(i)
                geo_status = "BREACH"
                ai_action = "GEOFENCE OVERRIDE"
                
        if i in breached_drones:
            geo_status = "LOCKED"
            if ai_action == "FLYING": 
                ai_action = "DESCENDING"
            
        print(f"D{i+1:<2} | {alt_val:<5.1f}m | {geo_status:<10} | {predicted_snr:<5.1f} dB (City) | {ai_action}")

    print("-" * 75)
    time.sleep(1)

print("\n[MISSION] Mission complete. Cutting remaining fleet throttle to 0%...")
for drone in fleet:
    drone.channels.overrides = {'3': 1000}
    drone.armed = False
    drone.close()
print("MISSION ENDED.")