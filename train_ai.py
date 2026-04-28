import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle
import warnings
warnings.filterwarnings("ignore") # Hides annoying math warnings

print("--- AEROGUARD-IQ: TRAINING AI BRAIN ---")
print("Reading flight_data.csv...")

# 1. Load the textbook you just created
df = pd.read_csv('flight_data.csv')

# 2. Separate the Inputs (Distance, Alt, Interference) from the Output (SNR)
X = df[['Distance_m', 'Altitude_m', 'Interference_Level']]
y = df['SNR_dB']

print("Training Random Forest algorithm. Please wait...")

# 3. Create and train the model (The "Black Box")
ai_model = RandomForestRegressor(n_estimators=50, random_state=42)
ai_model.fit(X, y)

# 4. Save the trained brain to a file so the control tower can use it
with open('aeroguard_brain.pkl', 'wb') as f:
    pickle.dump(ai_model, f)

print("[SUCCESS] AI Brain has been trained and saved as 'aeroguard_brain.pkl'!")