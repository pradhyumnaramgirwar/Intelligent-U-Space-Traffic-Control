import time
import dronekit_sitl
from dronekit import connect, VehicleMode

print("--- U-SPACE MISSION: THE BY-THE-BOOK FLIGHT ---")

print("[SYSTEM] Booting fresh virtual airspace...")
sitl = dronekit_sitl.SITL()
sitl.download('copter', '3.3', verbose=False)
sitl.launch(['--home=-35.363261,149.165230,584,0'], await_ready=True)

try:
    print("[LINK] Connecting to telemetry streams...")
    v = connect(sitl.connection_string(), wait_ready=False, heartbeat_timeout=9999)
    v._heartbeat_timeout = 9999
    
    # Keeping the wiretap active so we can hear the drone's thoughts
    @v.on_message('STATUSTEXT')
    def diagnostic_listener(self, name, message):
        print(f"   *** [DRONE INTERCOM] {message.text} ***")

    print("[LINK] Downloading parameter map (Waiting out the barometer)...")
    v.wait_ready(timeout=9999)
    print("[SUCCESS] Drone brain mapped!")

    print("\n[PRE-FLIGHT] Injecting Factory RC Calibration to pass safety checks...")
    # We DO NOT disable ARMING_CHECK. We let the drone protect itself.
    v.parameters['FS_THR_ENABLE'] = 0 # Only disable throttle failsafe
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
    print("   -> This will take 15-30 seconds. Do not interrupt it.")
    while not v.is_armable:
        print(f"   -> System Status: {v.system_status.state} | GPS: {v.gps_0.fix_type} | Math Engine Aligning...")
        time.sleep(4)
    print("   -> [SUCCESS] EKF Math Engine Aligned authentically!")

    print("\n*** GREEN LIGHT: READY TO FLY ***")
    
    print("[COMMAND] Requesting GUIDED mode...")
    v.mode = VehicleMode("GUIDED")
    while v.mode.name != 'GUIDED':
        print(f"   -> Mode is {v.mode.name}. Requesting GUIDED...")
        v.mode = VehicleMode("GUIDED")
        time.sleep(2)
    print("   -> MODE IS GUIDED!")
        
    print("\n[COMMAND] Arming motors...")
    v.armed = True
    while not v.armed:
        print("   -> Sending ARM command...")
        v.armed = True
        time.sleep(2)
    print("   -> MOTORS ARE LIVE!")

    print("\n!!! LIFT OFF !!!")
    v.simple_takeoff(10)

    for i in range(15):
        if v.location.global_relative_frame:
            print(f"   -> Altitude: {v.location.global_relative_frame.alt:.2f}m")
        time.sleep(1)

    print("\n[MISSION] Landing...")
    v.mode = VehicleMode("LAND")
    time.sleep(5)

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