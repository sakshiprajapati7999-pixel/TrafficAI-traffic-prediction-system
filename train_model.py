import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

print("========== Training Started ==========")

# -------------------------------
# Load Dataset
# -------------------------------

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, "dataset", "Traffic.csv")

print("Reading Dataset from:")
print(csv_path)

df = pd.read_csv(csv_path)

print("\nDataset Loaded Successfully")
print(df.head())

# -------------------------------
# Convert Time to Hour
# -------------------------------

df["Hour"] = pd.to_datetime(df["Time"]).dt.hour

# -------------------------------
# Encode Day
# -------------------------------

day_encoder = LabelEncoder()
df["Day"] = day_encoder.fit_transform(df["Day of the week"])

# -------------------------------
# Encode Target
# -------------------------------

traffic_encoder = LabelEncoder()
df["Traffic Situation"] = traffic_encoder.fit_transform(
    df["Traffic Situation"]
)

# -------------------------------
# Features & Target
# -------------------------------

X = df[
    [
        "Hour",
        "Day",
        "CarCount",
        "BikeCount",
        "BusCount",
        "TruckCount",
        "Total",
    ]
]

y = df["Traffic Situation"]

# -------------------------------
# Train Test Split
# -------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# -------------------------------
# Train Model
# -------------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# -------------------------------
# Prediction
# -------------------------------

pred = model.predict(X_test)

# -------------------------------
# Accuracy
# -------------------------------

accuracy = accuracy_score(y_test, pred)

print("\n===================================")
print("Accuracy :", round(accuracy * 100, 2), "%")
print("===================================\n")

print(classification_report(y_test, pred))

# -------------------------------
# Save Model
# -------------------------------

joblib.dump(
    model,
    os.path.join(base_dir, "traffic_model.pkl")
)

joblib.dump(
    day_encoder,
    os.path.join(base_dir, "day_encoder.pkl")
)

joblib.dump(
    traffic_encoder,
    os.path.join(base_dir, "traffic_encoder.pkl")
)

print("Model Saved Successfully!")
print("traffic_model.pkl")
print("day_encoder.pkl")
print("traffic_encoder.pkl")
print("\n========== Training Completed ==========")