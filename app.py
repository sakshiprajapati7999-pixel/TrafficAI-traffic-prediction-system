from flask import Flask, render_template, request
from db_config import get_connection
import joblib
import pandas as pd
from datetime import date
app = Flask(__name__)

# ===========================
# Load Machine Learning Model
# ===========================

model = joblib.load("traffic_model.pkl")
day_encoder = joblib.load("day_encoder.pkl")
traffic_encoder = joblib.load("traffic_encoder.pkl")

# ===========================
# Home Page
# ===========================

@app.route("/")
def home():
    return render_template("index.html")


# ===========================
# Login Page
# ===========================

from flask import request, redirect, url_for, render_template

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute(
            "SELECT * FROM users WHERE username=%s",
            (username,)
        )

        user = cursor.fetchone()

        if user:
            cursor.close()
            conn.close()
            return render_template(
                "login.html",
                error="Username already exists!"
            )

        # Save new user
        cursor.execute(
            "INSERT INTO users(username, password) VALUES(%s,%s)",
            (username, password)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("login.html")


# ===========================
# Dashboard
# ===========================

@app.route("/dashboard")
def dashboard():

  
  

    


    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ===========================
    # Total Predictions
    # ===========================

    cursor.execute("SELECT COUNT(*) AS total_predictions FROM predictions")
    total_predictions = cursor.fetchone()["total_predictions"]

    # ===========================
    # Total Cars
    # ===========================

    cursor.execute("SELECT SUM(car_count) AS total_cars FROM predictions")
    total_cars = cursor.fetchone()["total_cars"] or 0

    # ===========================
    # Total Bikes
    # ===========================

    cursor.execute("SELECT SUM(bike_count) AS total_bikes FROM predictions")
    total_bikes = cursor.fetchone()["total_bikes"] or 0

    # ===========================
    # Total Buses
    # ===========================

    cursor.execute("SELECT SUM(bus_count) AS total_buses FROM predictions")
    total_buses = cursor.fetchone()["total_buses"] or 0

    # ===========================
    # Total Trucks
    # ===========================

    cursor.execute("SELECT SUM(truck_count) AS total_trucks FROM predictions")
    total_trucks = cursor.fetchone()["total_trucks"] or 0

    # ===========================
    # Latest Status
    # ===========================

    cursor.execute("""
        SELECT traffic_status
        FROM predictions
        ORDER BY id DESC
        LIMIT 1
    """)

    latest = cursor.fetchone()

    if latest:
        latest_status = latest["traffic_status"]
    else:
        latest_status = "No Data"

    # ===========================
    # Vehicle Chart
    # ===========================

    cursor.execute("""
        SELECT
        SUM(car_count) AS cars,
        SUM(bike_count) AS bikes,
        SUM(bus_count) AS buses,
        SUM(truck_count) AS trucks
        FROM predictions
    """)

    chart = cursor.fetchone()

    cars = chart["cars"] or 0
    bikes = chart["bikes"] or 0
    buses = chart["buses"] or 0
    trucks = chart["trucks"] or 0

    # ===========================
    # Recent Predictions
    # ===========================

    cursor.execute("""
        SELECT *
        FROM predictions
        ORDER BY id DESC
        LIMIT 5
    """)

    recent_predictions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(

        "dashboard.html",

        total_predictions=total_predictions,

        total_cars=total_cars,

        total_bikes=total_bikes,

        total_buses=total_buses,

        total_trucks=total_trucks,

        latest_status=latest_status,

        cars=cars,

        bikes=bikes,

        buses=buses,

        trucks=trucks,

        recent_predictions=recent_predictions
    )


# ===========================
# Prediction Page
# ===========================

@app.route("/prediction", methods=["GET", "POST"])
def prediction():

    prediction = None
    history = []

    if request.method == "POST":

        try:

            # ===========================
            # Get Form Data
            # ===========================

            day = request.form["day"]
            hour = int(request.form["hour"])

            car = int(request.form["car"])
            bike = int(request.form["bike"])
            bus = int(request.form["bus"])
            truck = int(request.form["truck"])

            total = car + bike + bus + truck

            # ===========================
            # Encode Day
            # ===========================

            day_encoded = day_encoder.transform([day])[0]

            # ===========================
            # Prepare Input
            # ===========================

            input_data = pd.DataFrame([[
                hour,
                day_encoded,
                car,
                bike,
                bus,
                truck,
                total
            ]],
            columns=[
                "Hour",
                "Day",
                "CarCount",
                "BikeCount",
                "BusCount",
                "TruckCount",
                "Total"
            ])

            # ===========================
            # Prediction
            # ===========================

            pred = model.predict(input_data)

            prediction = traffic_encoder.inverse_transform(pred)[0]

            # ===========================
            # Save Prediction
            # ===========================

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO predictions
            (
                prediction_date,
                predicted_count,
                hour,
                traffic_status,
                day_name,
                car_count,
                bike_count,
                bus_count,
                truck_count,
                total
            )

            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

            """,
            (
                date.today(),
                total,
                hour,
                prediction,
                day,
                car,
                bike,
                bus,
                truck,
                total
            ))

            conn.commit()

            cursor.close()
            conn.close()

        except Exception as e:

            prediction = str(e)

    # ===========================
    # Prediction History
    # ===========================

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM predictions
        ORDER BY id DESC
        LIMIT 10
    """)

    history = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "prediction.html",
        prediction=prediction,
        history=history
    )
            

            

# ===========================
# Reports
# ===========================

@app.route("/reports")
def reports():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get Filters
    selected_date = request.args.get("date")
    selected_status = request.args.get("status")

    query = "SELECT * FROM predictions WHERE 1=1"
    values = []

    # Date Filter
    if selected_date:
        query += " AND prediction_date=%s"
        values.append(selected_date)

    # Status Filter
    if selected_status:
        query += " AND traffic_status=%s"
        values.append(selected_status)

    query += " ORDER BY id DESC"

    cursor.execute(query, values)

    reports = cursor.fetchall()

    # ==========================
    # Total Reports
    # ==========================

    cursor.execute("SELECT COUNT(*) AS total FROM predictions")
    total_reports = cursor.fetchone()["total"]

    # ==========================
    # Heavy Reports
    # ==========================

    cursor.execute("""
        SELECT COUNT(*) AS heavy
        FROM predictions
        WHERE traffic_status='Heavy'
    """)

    heavy_reports = cursor.fetchone()["heavy"]

    # ==========================
    # Normal Reports
    # ==========================

    cursor.execute("""
        SELECT COUNT(*) AS normal
        FROM predictions
        WHERE traffic_status='Normal'
    """)

    normal_reports = cursor.fetchone()["normal"]

    cursor.close()
    conn.close()

    return render_template(

        "reports.html",

        reports=reports,

        total_reports=total_reports,

        heavy_reports=heavy_reports,

        normal_reports=normal_reports,

        selected_date=selected_date,

        selected_status=selected_status

    )

# ===========================
# Analytics
# ===========================

@app.route("/analytics")
def analytics():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ===========================
    # Total Predictions
    # ===========================

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM predictions
    """)

    total_predictions = cursor.fetchone()["total"]

    # ===========================
    # Heavy Traffic
    # ===========================

    cursor.execute("""
        SELECT COUNT(*) AS heavy
        FROM predictions
        WHERE traffic_status='Heavy'
    """)

    heavy = cursor.fetchone()["heavy"]

    # ===========================
    # High Traffic
    # ===========================

    cursor.execute("""
        SELECT COUNT(*) AS high
        FROM predictions
        WHERE traffic_status='High'
    """)

    high = cursor.fetchone()["high"]

    # ===========================
    # Normal Traffic
    # ===========================

    cursor.execute("""
        SELECT COUNT(*) AS normal
        FROM predictions
        WHERE traffic_status='Normal'
    """)

    normal = cursor.fetchone()["normal"]

    # ===========================
    # Low Traffic
    # ===========================

    cursor.execute("""
        SELECT COUNT(*) AS low
        FROM predictions
        WHERE traffic_status='Low'
    """)

    low = cursor.fetchone()["low"]

    # ===========================
    # Vehicle Totals
    # ===========================

    cursor.execute("""

        SELECT

        SUM(car_count) AS cars,

        SUM(bike_count) AS bikes,

        SUM(bus_count) AS buses,

        SUM(truck_count) AS trucks

        FROM predictions

    """)

    vehicle = cursor.fetchone()

    cars = vehicle["cars"] or 0
    bikes = vehicle["bikes"] or 0
    buses = vehicle["buses"] or 0
    trucks = vehicle["trucks"] or 0

    # ===========================
    # Recent Predictions
    # ===========================

    cursor.execute("""

        SELECT *

        FROM predictions

        ORDER BY id DESC

        LIMIT 10

    """)

    recent_predictions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(

        "analytics.html",

        total_predictions=total_predictions,

        heavy=heavy,

        high=high,

        normal=normal,

        low=low,

        cars=cars,

        bikes=bikes,

        buses=buses,

        trucks=trucks,

        recent_predictions=recent_predictions

    )

# ===========================
# Run App
# ===========================

if __name__ == "__main__":
    app.run(debug=True)