import subprocess
import time
import sys
import os
import shutil

print("--- U-SPACE: FLEET SPAWNER ---")

base_lat = -35.363261
base_lon = 149.165230
processes = []

for i in range(3):
    folder_name = f"drone_{i+1}_data"
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)

for i in range(3):
    offset_lon = base_lon + (i * 0.0001)
    home_str = f"{base_lat},{offset_lon},584,0"
    tcp_port = 5760 + (i * 10)
    
    print(f"[SYSTEM] Booting Drone {i+1} | TCP: {tcp_port}")
    
    # We removed the rejected commands so the binary actually boots!
    cmd = [
        sys.executable, "-m", "dronekit_sitl", "copter-3.3",
        f"-I{i}", 
        f"--home={home_str}"
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
    for p in processes:
        p.terminate()