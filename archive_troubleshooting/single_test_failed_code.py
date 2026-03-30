import time
import dronekit_sitl
from dronekit import connect, VehicleMode

print("--- THE EMERGENCY BYPASS TEST (V2) ---")

# 1. Launch the simulator
print("Booting local simulator...")
sitl = dronekit_sitl.SITL()
sitl.download('copter', '3.3', verbose=False)
# Launch with skip-calibration and fixed port
sitl.launch(['--home=-35.363261,149.165230,584,0', '-gs'], await_ready=True)

# THE FIX: Give Windows 10 seconds to actually open the network port
print("Waiting 10 seconds for network ports to open...")
time.sleep(10)

# 2. Connection with Retry Logic
print("Connecting to telemetry...")
vehicle = None
while vehicle is None:
    try:
        vehicle = connect(sitl.connection_string(), wait_ready=True, timeout=60)
    except Exception as e:
        print(f"Waiting for connection... ({e})")
        time.sleep(2)

print("Connected! Disabling hardware checks...")
vehicle.parameters['ARMING_CHECK'] = 0
vehicle.parameters['FS_GCS_ENABLE'] = 0
time.sleep(1)

print("Waiting for GPS lock...")
while vehicle.gps_0.fix_type < 3:
    time.sleep(1)

print("Forcing Home Location...")
vehicle.home_location = vehicle.location.global_frame
time.sleep(2)

print("Forcing GUIDED mode...")
while vehicle.mode.name != 'GUIDED':
    print(f"   -> Current: {vehicle.mode.name}. Retrying GUIDED...")
    vehicle._master.set_mode(4) 
    time.sleep(2)

print("Mode is GUIDED! Arming...")
while not vehicle.armed:
    print("   -> Sending ARM...")
    vehicle.armed = True
    time.sleep(2)

print("LIFT OFF!")
vehicle.simple_takeoff(10)

for i in range(15):
    if vehicle.location.global_relative_frame:
        print(f"Altitude: {vehicle.location.global_relative_frame.alt:.2f}m")
    time.sleep(1)

print("Landing...")
vehicle._master.set_mode(9)
time.sleep(5)

vehicle.close()
sitl.stop()
