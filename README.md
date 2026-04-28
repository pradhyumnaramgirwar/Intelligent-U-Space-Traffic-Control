Intelligent U-Space Traffic Control Architecture
Intelligent U-Space Traffic Control Architecture is a comprehensive, distributed Software-In-The-Loop (SITL) simulation for autonomous UAV fleet management. Built from the ground up to bypass standard API limitations, this system utilizes direct MAVLink TCP injection, real-time asynchronous telemetry matrices, and a predictive Machine Learning layer to autonomously enforce safe Beyond Visual Line of Sight (BVLOS) airspace operations.

🚀 System Architecture & Development Phases
Phase 1: Low-Level MAVLink API Bypass
During initial development, a critical routing bug was identified in the standard DroneKit-Python library on Windows, which silently dropped high-level autonomous navigation commands (failing to translate "GUIDED" into the correct MAVLink ENUM machine code).

The Solution: Rather than relying on broken API wrappers, the system bypasses autonomous modes entirely. It forces authentic EKF (Extended Kalman Filter) alignment, injects factory RC calibration data directly into the virtual EEPROM, and uses direct MAVLink channel overrides to arm the motors and physically push throttle commands in manual STABILIZE mode.

Phase 2: Filesystem Isolation & Swarm Deployment
To simulate a true U-Space environment, the architecture was expanded to control a synchronized fleet of 3 drones.

The Engineering Challenge: Booting multiple ArduPilot SITL instances in a single directory causes a fatal resource contention error. Drones "tug-of-war" over the same virtual EEPROM file, causing subsequent drones to fail their Compass and Accelerometer pre-arm checks.

The Solution: fleet_spawner.py uses Python's subprocess and os modules to dynamically generate isolated workspace directories for each flight controller. The control tower then iterates across sequential TCP ports (5760, 5770, 5780) to align the fleet's EKFs in parallel and inject synchronized MAVLink throttle overrides for a simultaneous swarm takeoff.

Phase 3: The Telemetry Radar Matrix
For an autonomous traffic control system to prevent collisions, it requires real-time state vectors for every aircraft in the airspace without network bottlenecking.

The Solution: The control script acts as a centralized radar hub. Using a synchronized polling loop, the system continuously extracts the global_relative_frame (Latitude, Longitude, Altitude) and groundspeed from each drone via their individual TCP MAVLink streams. This raw data is compiled into a live, low-latency terminal matrix, serving as the sensory input for the avoidance algorithms.

Phase 4: Predictive AI & Autonomous Safety Overrides
The final phase introduces a multi-layered autonomous safety system designed to prevent both physical collisions and communication link failures.

Physical Safety (Geofencing & Proximity): The system calculates 3D spatial separation between dynamic swarm agents using Haversine trigonometry. If drones breach a strict 15-meter proximity limit or cross a static GPS geofence, the system executes a sub-second 0% throttle emergency override.

Predictive AI (Signal Integrity): A Random Forest Machine Learning model (scikit-learn) was trained on a 2,000-row synthetic dataset simulating drone flight parameters. The AI actively parses live telemetry (altitude, distance, urban interference) to predict dynamic Signal-to-Noise Ratio (SNR) degradation. If the model predicts an imminent communication failure (SNR < 45dB), it autonomously grounds the aircraft before the connection is actually lost.

💻 Installation & Usage
Prerequisites
Ensure you have Python installed, along with the required libraries:

Bash
pip install dronekit pymavlink pandas scikit-learn
Running the Simulation
Step 1: Spawn the Fleet
Run the spawner to generate isolated ArduPilot SITL instances and boot the virtual flight controllers.

Bash
python fleet_spawner.py
Step 2: Initialize the Control Tower
(Open a new terminal window). Run the final traffic controller script to connect to the fleet, load the Machine Learning model, and execute the autonomous flight protocol.

Bash
python fleet_traffic_controller_v5.py
📂 Repository Structure
fleet_spawner.py: Subprocess manager for generating isolated SITL nodes.

fleet_traffic_controller_v1.py -> v4.py: Architectural stepping stones documenting the progression from single-drone bypass to multi-drone radar.

fleet_traffic_controller_v5.py: The final production script featuring the complete ML predictive model and safety geofence.

generate_dataset.py: Script to generate synthetic flight data.

flight_data.csv: The 2,000-row dataset mapping altitude/distance to radio interference.

train_ai.py: Script utilizing pandas and scikit-learn to train the regression model.

aeroguard_brain.pkl: The serialized, pre-trained Random Forest AI model.
