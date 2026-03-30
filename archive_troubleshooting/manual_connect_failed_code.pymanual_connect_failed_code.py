import time
from dronekit import connect, VehicleMode

print("--- U-SPACE MISSION: THE EKF FIX ---")

def connect_with_patience():
    print("Connecting to drone on TCP port 5760...")
    vehicle = connect('tcp:127.0.0.1:5760', wait_ready=False, heartbeat_timeout=9999)
    vehicle._heartbeat_timeout = 9999 
    
    print("[LINK] Physical link open. Waiting for the drone to wake up...")
    while True:
        try:
            if vehicle.last_heartbeat < 2 and vehicle.last_heartbeat != -1:
                print("[SUCCESS] Heartbeat detected!")
                break
            time.sleep(2)
        except Exception:
            pass
            
    print("[LINK] Downloading parameter map from drone memory...")
    vehicle.wait_ready(timeout=9999)
    print("[SUCCESS] Drone brain fully mapped to Python!")
    return vehicle

try:
    v = connect_with_patience()

    print("\n[PRE-FLIGHT] Disabling strict hardware safety checks globally...")
    v.parameters['ARMING_CHECK'] = 0
    v.parameters['FS_THR_ENABLE'] = 0
    time.sleep(1)

    # ---> THE RC FACTORY RESET <---
    print("[PRE-FLIGHT] Injecting Factory RC Calibration data...")
    for i in range(1, 5):
        v.parameters[f'RC{i}_MIN'] = 1000
        v.parameters[f'RC{i}_MAX'] = 2000
        v.parameters[f'RC{i}_TRIM'] = 1500
    # ------------------------------

    print("\n[PRE-FLIGHT] Waiting for GPS 3D Fix...")
    while v.gps_0.fix_type is None or v.gps_0.fix_type < 3:
        time.sleep(2)
    print("   -> [SUCCESS] GPS 3D Lock Acquired!")

    # ---> THE EKF BAKE TIME <---
    print("\n[PRE-FLIGHT] Allowing EKF Math Engine to align (15 seconds)...")
    for x in range(15, 0, -1):
        print(f"   -> Baking EKF... {x}s remaining")
        time.sleep(1)
    # ---------------------------

    print("\n*** GREEN LIGHT: READY TO FLY ***")
    
    print("[COMMAND] Registering Home Location...")
    while not v.location.global_frame.lat:
        time.sleep(1)
    v.home_location = v.location.global_frame
    print(f"   -> Home locked at: {v.home_location.lat}, {v.home_location.lon}")
    
    print("[COMMAND] Turning on Virtual Remote Control...")
    v.channels.overrides = {'1': 1500, '2': 1500, '3': 1000, '4': 1500}
    time.sleep(2)
    
    print("[COMMAND] Requesting GUIDED mode...")
    while v.mode.name != 'GUIDED':
        print(f"   -> Drone says: {v.mode.name}. Requesting GUIDED...")
        v.mode = VehicleMode("GUIDED")
        time.sleep(2)
        
    print("\n[COMMAND] Mode is GUIDED! Arming motors...")
    while not v.armed:
        print("   -> Sending ARM command...")
        v.armed = True
        time.sleep(2)

    print("\n!!! LIFT OFF !!!")
    v.simple_takeoff(10)

    for i in range(15):
        if v.location.global_relative_frame:
            print(f"   -> Altitude: {v.location.global_relative_frame.alt:.2f}m")
        time.sleep(1)

    print("\n[MISSION] Landing...")
    v.mode = VehicleMode("LAND")

except Exception as e:
    print(f"\n[CRITICAL ERROR] {e}")

input("\nMISSION ENDED. Press Enter to close...")
