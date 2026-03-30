import time
import dronekit_sitl
import psutil # We use this to check if the process is alive
from dronekit import connect, VehicleMode

print("--- DIAGNOSTIC FLIGHT TEST ---")

# 1. Kill everything first to be 100% sure
import os
os.system('taskkill /f /im arducopter.exe >nul 2>&1')

# 2. Launch the simulator
print("Attempting to boot the simulator...")
sitl = dronekit_sitl.SITL()
sitl.download('copter', '3.3', verbose=False)
sitl.launch(['--home=-35.363261,149.165230,584,0'], await_ready=True)

# 3. Process Health Check
print("Checking if 'arducopter.exe' is actually running...")
time.sleep(5)
is_running = False
for proc in psutil.process_iter(['name']):
    if 'arducopter' in proc.info['name'].lower():
        is_running = True
        print(f"   -> FOUND IT! Process ID: {proc.pid}")

if not is_running:
    print("!!! CRITICAL ERROR: The simulator crashed immediately after launching.")
    print("This is usually a Windows permissions issue or a missing C++ library.")
else:
    # 4. Connection with Heartbeat
    print("Process is alive. Attempting to connect to TCP port 5760...")
    try:
        # We manually specify the local address to bypass Windows DNS issues
        vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True, timeout=30)
        print("CONNECTED!")
        
        # Simple takeoff test
        vehicle.parameters['ARMING_CHECK'] = 0
        print("Taking off...")
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True
        vehicle.simple_takeoff(10)
        
        time.sleep(10)
        vehicle.close()
    except Exception as e:
        print(f"FAILED TO CONNECT: {e}")

sitl.stop()