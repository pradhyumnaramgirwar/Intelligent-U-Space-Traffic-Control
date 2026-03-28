from dronekit import connect
import dronekit_sitl

print("Starting the U-Space simulator...")
# 1. Start the simulator
sitl = dronekit_sitl.start_default()
connection_string = sitl.connection_string()

# 2. Connect to the virtual drone
print(f"Connecting to drone on: {connection_string}")
vehicle = connect(connection_string, wait_ready=True)

# 3. Print the drone's status
print(f"SUCCESS! Drone is ready.")
print(f"Current GPS Location: {vehicle.location.global_frame}")
print(f"Battery Level: {vehicle.battery.level}%")

# 4. Close the connection
vehicle.close()
sitl.stop()
print("Test complete and connection closed.")