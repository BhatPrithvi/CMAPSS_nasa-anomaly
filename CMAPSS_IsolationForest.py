import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import os
os.makedirs("/app/output/plots", exist_ok=True)  # create folder inside container

Columns = ['unit_number', 'time', 'operational_setting_1', 'operations_setting_2', 'operational_setting_3'] + [f'_sensor_{i}' for i in range(1,22)]
TrainData = pd.read_csv("train_FD001.txt", sep = r"\s+", header = None, names=Columns)
TestData = pd.read_csv("test_FD001.txt", sep = r"\s+", header = None, names=Columns)

SensorColumns = [col for col in TrainData.columns if 'sensor' in col]

#Initialize the model
model = IsolationForest(n_estimators=100,contamination=0.05, random_state=42)
model.fit(TrainData[SensorColumns])

TrainPreds=model.predict(TrainData[SensorColumns])
TestPreds=model.predict(TestData[SensorColumns]) 


#Add anamolies to the dataset
TrainData['anomaly'] = TrainPreds
TestData['anomaly'] = TestPreds

#Filter anamolies
TrainAnomaly=TrainData[TrainData['anomaly'] == -1]
TestAnomaly=TestData[TestData['anomaly'] == -1]

for col in SensorColumns:
    plt.figure(figsize=(8,4))
    plt.plot(TrainData.index, TrainData[col], label="Sensor values")
    plt.scatter(TrainAnomaly.index, TrainAnomaly[col], color='red', label='Anomalies')
    plt.title(f"Isolation Forest - {col}")
    plt.legend()
    plt.savefig(f"/app/output/plots/anomaly_plot_train{col}.png")  # save to a folder inside container
    plt.close()


for col in SensorColumns:
    plt.figure(figsize=(8,4))
    plt.plot(TestData.index, TestData[col], label="Sensor values")
    plt.scatter(TestAnomaly.index, TestAnomaly[col], color='red', label='Anomalies')
    plt.title(f"Isolation Forest - {col}")
    plt.legend()    
    plt.savefig(f"/app/output/plots/anomaly_plot_test{col}.png")  # save to a folder inside container
    plt.close()

TrainAnomaly.to_csv('/app/output/TrainAnomalyResults.csv')
TestAnomaly.to_csv('/app/output/TestAnomalyResults.csv')

print("Anomaly Detection complete")

from flask import Flask, jsonify

app = Flask(__name__) # Initializes a Flask application. This is the entry point for the web service.

# Defines the root endpoint (/) which responds with a simple text message. Conforms service is running
@app.route("/") 
def hello():
    return "Hello from CMAPSS Isolation Forest"

# Defines an endpoint that returns basic system statistics (CPU, memory usage) in JSON. This makes the service observable and easy to integrate with monitoring tools (like Prometheus).
@app.route("/metrics")
def metrics():
    # Optional: return some basic stats
    return jsonify({
        "CPU": psutil.cpu_percent(),
        "Memory": psutil.virtual_memory().percent
    })

# Runs the Flask app on all available network interfaces inside the container (0.0.0.0) and binds it to port 8000. This ensures the service is accessible externally when Docker/Kubernetes expose it.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)


