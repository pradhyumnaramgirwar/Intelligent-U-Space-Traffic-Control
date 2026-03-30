import time
import dronekit_sitl
from dronekit import connect

print("--- U-SPACE MISSION: THE VIRTUAL PILOT ---")

print("[SYSTEM] Booting fresh virtual airspace...")
sitl = dronekit_sitl.SITL()
sitl.download('copter', '3.3', verbose=False)
sitl.launch(['--home=-35.363261,149.165230,584,0'], await_ready=True)

try:
    print("[LINK] Connecting to telemetry streams...")
    v = connect(sitl.connection_string(), wait_ready=False, heartbeat_timeout=9999)
    v._heartbeat_timeout = 9999
    
    @v.on_message('STATUSTEXT')
    def diagnostic_listener(self, name, message):
        print(f"   *** [DRONE INTERCOM] {message.text} ***")

    print("[LINK] Downloading parameter map (Waiting out the barometer)...")
    v.wait_ready(timeout=9999)
    print("[SUCCESS] Drone brain mapped!")

    print("\n[PRE-FLIGHT] Injecting Factory RC Calibration...")
    v.parameters['FS_THR_ENABLE'] = 0 
    for i in range(1, 5):
        v.parameters[f'RC{i}_MIN'] = 1000
        v.parameters[f'RC{i}_MAX'] = 2000
        v.parameters[f'RC{i}_TRIM'] = 1500
    time.sleep(2)

    print("\n[PRE-FLIGHT] Waiting for GPS 3D Fix...")
    while v.gps_0.fix_type is None or v.gps_0.fix_type < 3:
        time.sleep(2)
    print("   -> [SUCCESS] GPS Lock Acquired!")

    print("\n[PRE-FLIGHT] Waiting for authentic Green Light (EKF Alignment)...")
    while not v.is_armable:
        print(f"   -> System Status: {v.system_status.state} | Aligning...")
        time.sleep(4)
    print("   -> [SUCCESS] EKF Math Engine Aligned!")

    print("\n*** GREEN LIGHT: READY TO FLY ***")
    
    # ---> THE MANUAL FLIGHT SEQUENCE <---
    print("[COMMAND] Grabbing Virtual Joysticks (Throttle to 0%)...")
    v.channels.overrides = {'1': 1500, '2': 1500, '3': 1000, '4': 1500}
    time.sleep(2)

    print("\n[COMMAND] Arming motors in manual STABILIZE mode...")
    v.armed = True
    while not v.armed:
        print("   -> Sending ARM command...")
        v.armed = True
        time.sleep(2)
    print("   -> MOTORS ARE SPINNING!")

    print("\n!!! PUSHING THROTTLE TO 80% !!!")
    # Channel 3 is Throttle. 1000 is off, 1500 is hover, 2000 is max.
    v.channels.overrides = {'3': 1800}

    # Watch the altitude climb!
    for i in range(15):
        if v.location.global_relative_frame:
            print(f"   -> Altitude: {v.location.global_relative_frame.alt:.2f}m")
        time.sleep(1)

    print("\n[MISSION] Cutting throttle to 0% to land...")
    v.channels.overrides = {'3': 1000}
    time.sleep(5)
    
    print("[MISSION] Disarming motors...")
    v.armed = False

except Exception as e:
    print(f"\n[CRITICAL ERROR] {e}")

finally:
    print("\n[SYSTEM] Closing airspace and killing simulator...")
    try:
        v.close()
    except:
        pass
    sitl.stop()
    input("MISSION ENDED. Press Enter to close...")