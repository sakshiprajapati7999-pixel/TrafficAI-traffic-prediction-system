import os
import joblib
import pandas as pd

# Base Directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load Model
model = joblib.load(os.path.join(base_dir, "traffic_model.pkl"))
day_encoder = joblib.load(os.path.join(base_dir, "day_encoder.pkl"))
traffic_encoder = joblib.load(os.path.join(base_dir, "traffic_encoder.pkl"))

# Sample Input
hour = 9
day = "Tuesday"
car = 120
bike = 25
bus = 15
truck = 10

total = car + bike + bus + truck

# Encode Day
day = day_encoder.transform([day])[0]

# Create DataFrame
sample = pd.DataFrame(
    [[hour, day, car, bike, bus, truck, total]],
    columns=[
        "Hour",
        "Day",
        "CarCount",
        "BikeCount",
        "BusCount",
        "TruckCount",
        "Total",
    ],
)

# Predict
prediction = model.predict(sample)

# Decode Result
result = traffic_encoder.inverse_transform(prediction)

print("\n==============================")
print("Predicted Traffic :", result[0])
print("==============================")