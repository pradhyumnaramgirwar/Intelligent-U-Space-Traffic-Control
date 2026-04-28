import subprocess
import time
import sys

print("--- U-SPACE: FLEET SPAWNER ---")

# Base coordinates (The virtual runway)
base_lat = -35.363261
base_lon = 149.165230

processes = []

# Boot 3 drones
for i in range(3):
    # Shift longitude slightly for each drone so they spawn ~10 meters apart side-by-side
    offset_lon = base_lon + (i * 0.0001)
    home_str = f"{base_lat},{offset_lon},584,0"
    
    port = 5760 + (i * 10)
    print(f"[SYSTEM] Booting Drone {i+1} on TCP Port {port}...")
    
    # We use Python to run the dronekit-sitl command line tool in the background
    cmd = [
        sys.executable, "-m", "dronekit_sitl", "copter-3.3",
        f"-I{i}", 
        f"--home={home_str}",
        "-w" # Wipe memory for a clean factory start
    ]
    
    # Popen runs the process without freezing our Python script
    p = subprocess.Popen(cmd)
    processes.append(p)
    time.sleep(2) # Stagger the boot times slightly so the CPU doesn't choke

print("\n[SUCCESS] 3 Virtual Drones are now active in the background.")
print("Leave this terminal open to keep the airspace alive.")
print("Press Ctrl+C to shut down the entire fleet.")

try:
    # Keep the script running to keep the background drones alive
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[SYSTEM] ATC shutting down the airspace...")
    for p in processes:
        p.terminate()
    print("Fleet terminated cleanly.")