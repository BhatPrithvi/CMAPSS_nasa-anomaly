from flask import Flask, jsonify
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import psutil
import os

app = Flask(__name__)

# ----------------------------
# ML TRAINING (runs once)
# ----------------------------
def train_model():
    os.makedirs("/app/output/plots", exist_ok=True)

    Columns = ['unit_number', 'time', 'operational_setting_1', 'operations_setting_2', 'operational_setting_3'] \
              + [f'sensor_{i}' for i in range(1, 22)]
    
    # Load datasets
    TrainData = pd.read_csv("train_FD001.txt", sep=r"\s+", header=None, names=Columns)
    TestData = pd.read_csv("test_FD001.txt", sep=r"\s+", header=None, names=Columns)

    SensorColumns = [col for col in TrainData.columns if 'sensor' in col]

    # Initialize and fit model
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(TrainData[SensorColumns])

    TrainData['anomaly'] = model.predict(TrainData[SensorColumns])
    TestData['anomaly'] = model.predict(TestData[SensorColumns])

    # Filter anomalies
    TrainAnomaly = TrainData[TrainData['anomaly'] == -1]
    TestAnomaly = TestData[TestData['anomaly'] == -1]

    # Save anomaly plots
    for col in SensorColumns:
        plt.figure(figsize=(8, 4))
        plt.plot(TrainData.index, TrainData[col], label="Sensor values")
        plt.scatter(TrainAnomaly.index, TrainAnomaly[col], color='red', label='Anomalies')
        plt.title(f"Isolation Forest - {col} (Train)")
        plt.legend()
        plt.savefig(f"/app/output/plots/anomaly_plot_train_{col}.png")
        plt.close()

    for col in SensorColumns:
        plt.figure(figsize=(8, 4))
        plt.plot(TestData.index, TestData[col], label="Sensor values")
        plt.scatter(TestAnomaly.index, TestAnomaly[col], color='red', label='Anomalies')
        plt.title(f"Isolation Forest - {col} (Test)")
        plt.legend()
        plt.savefig(f"/app/output/plots/anomaly_plot_test_{col}.png")
        plt.close()

    # Save results to CSV
    TrainAnomaly.to_csv('/app/output/TrainAnomalyResults.csv')
    TestAnomaly.to_csv('/app/output/TestAnomalyResults.csv')

    print("Anomaly Detection complete")
    return model, TrainAnomaly, TestAnomaly


# Run ML once at startup
MODEL, TRAIN_ANOMALY, TEST_ANOMALY = train_model()


# ----------------------------
# FLASK ROUTES
# ----------------------------
@app.route("/")
def hello():
    return "Hello from CMAPSS Isolation Forest (model already trained ✅)"


@app.route("/metrics")
def metrics():
    return jsonify({
        "CPU": psutil.cpu_percent(),
        "Memory": psutil.virtual_memory().percent
    })


@app.route("/results")
def results():
    """Return summary stats from anomaly detection"""
    return jsonify({
        "Train_Anomalies": len(TRAIN_ANOMALY),
        "Test_Anomalies": len(TEST_ANOMALY),
        "Message": "Anomaly detection completed and results saved in /app/output"
    })


# ----------------------------
# MAIN ENTRY POINT
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
