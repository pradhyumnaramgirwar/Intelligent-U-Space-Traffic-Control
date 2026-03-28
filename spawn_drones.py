import os
import time
import subprocess
from dronekit import connect

print("Starting U-Space Airspace Simulator...")

# Create separate folders for the drones
os.makedirs("drone1_data", exist_ok=True)
os.makedirs("drone2_data", exist_ok=True)

# 1. Launch Drones as completely separate background programs!
print("Launching Drone 1 (Instance 0) in the background...")
drone1_process = subprocess.Popen(["py", "-m", "dronekit_sitl", "copter", "--instance", "0"], cwd="drone1_data")

print("Launching Drone 2 (Instance 1) in the background...")
drone2_process = subprocess.Popen(["py", "-m", "dronekit_sitl", "copter", "--instance", "1"], cwd="drone2_data")

# Give Windows a solid 10 seconds to boot both programs fully
print("Waiting 10 seconds for both simulators to fully boot up...")
time.sleep(10)

# 2. Connect to the drones
print("Connecting to Drone 1 on tcp:127.0.0.1:5760...")
drone1 = connect('tcp:127.0.0.1:5760', wait_ready=True)

print("Connecting to Drone 2 on tcp:127.0.0.1:5770...")
drone2 = connect('tcp:127.0.0.1:5770', wait_ready=True)

# 3. Print the Radar Status
print("\n--- U-SPACE RADAR ONLINE ---")
print(f"Drone 1 Location: {drone1.location.global_frame}")
print(f"Drone 2 Location: {drone2.location.global_frame}")
print("----------------------------\n")

# 4. Clean up safely
print("Test successful! Closing connections...")
drone1.close()
drone2.close()

print("Shutting down background simulators...")
drone1_process.terminate()
drone2_process.terminate()
print("Simulation ended safely.")