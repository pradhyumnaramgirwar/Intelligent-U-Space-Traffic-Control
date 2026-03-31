import subprocess
import time
import sys
import os
import shutil

print("--- U-SPACE: NON-DESTRUCTIVE FLEET SPAWNER ---")

base_lat = -35.363261
base_lon = 149.165230

processes = []

# Clean up old data folders if they exist
for i in range(3):
    folder_name = f"drone_{i+1}_data"
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)

# Boot 3 isolated drones WITHOUT wiping their factory calibration
for i in range(3):
    offset_lon = base_lon + (i * 0.0001)
    home_str = f"{base_lat},{offset_lon},584,0"
    port = 5760 + (i * 10)
    
    print(f"[SYSTEM] Booting Drone {i+1} on Port {port}...")
    
    cmd = [
        sys.executable, "-m", "dronekit_sitl", "copter-3.3",
        f"-I{i}", 
        f"--home={home_str}"
        # Notice: The "-w" flag has been DELETED!
    ]
    
    p = subprocess.Popen(cmd, cwd=f"drone_{i+1}_data")
    processes.append(p)
    time.sleep(2) 

print("\n[SUCCESS] 3 Virtual Drones are now active.")
print("Leave this terminal open. Press Ctrl+C to shut down.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[SYSTEM] ATC shutting down the airspace...")
    for p in processes:
        p.terminate()
    print("Fleet terminated cleanly.")