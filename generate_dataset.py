import csv
import random

print("--- AEROGUARD-IQ: SYNTHETIC DATA GENERATOR ---")
print("Generating 2,000 flight records for the AI Brain...")

# Create a new Excel-style CSV file
with open('flight_data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write the column headers
    writer.writerow(['Distance_m', 'Altitude_m', 'Interference_Level', 'SNR_dB'])

    # Generate 2,000 fake flights
    for _ in range(2000):
        # Random flight parameters
        distance = random.uniform(10, 2000)      # Drone is between 10m and 2km away
        altitude = random.uniform(5, 150)        # Drone is between 5m and 150m high
        interference = random.choice([0, 1, 2])  # 0=Low, 1=Medium, 2=High (like city buildings)
        
        # The secret physics formula: SNR drops with distance and interference, but improves with altitude
        snr = 100 - (distance * 0.03) - (interference * 15) + (altitude * 0.1)
        
        # Add a little random "wind noise" so the AI has to work hard to learn the pattern
        snr += random.uniform(-5, 5)
        
        # Keep SNR locked between 0 (Dead) and 100 (Perfect)
        snr = max(0, min(100, snr))

        # Save the row
        writer.writerow([round(distance, 2), round(altitude, 2), interference, round(snr, 2)])

print("[SUCCESS] 'flight_data.csv' has been created in your folder!")
print("The textbook is ready. We can now train the AI.")