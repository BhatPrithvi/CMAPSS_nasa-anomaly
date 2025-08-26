import pandas as pd
import matplotlib.pyplot as plt
import os
import logging
import psutil
import time
import sys


from sklearn.ensemble import IsolationForest
from prometheus_client import start_http_server, Gauge

# Start Prometheus metrics server on port 8000
start_http_server(8000, addr='0.0.0.0')

# Define metrics
# Gauges are exported as metrics (usually via an HTTP /metrics endpoint when start_http_server(port) is started from prometheus_client).
AnomalyCountTrain = Gauge('AnomalyCountTrain', 'Number of anomalies detected in train data')
AnomalyCountTest= Gauge('AnomalyCountTest', 'Number of anomalies detected in test data')
CpuUsage = Gauge('CpuUsagePercent','CPU usage percent')
MemoryUsage = Gauge('MemoryUsagePercent', 'Memory usage percent')

os.makedirs("/app/output", exist_ok=True)
os.makedirs("/app/output/plots", exist_ok=True)  # create folder inside container

log_path = "/app/output/Anomaly.log"

# Remove existing handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, mode='w'),
        logging.StreamHandler(sys.stdout)    
    ],
    force=True

)

# Tracking CPU/Memory usage
CpuPercent = psutil.cpu_percent(interval=1)  # Average CPU usage over 1 second
Mem = psutil.virtual_memory() # Returns tuple with details about system RAM e.g Total physical RAM, available RAM, percentage of RAM currently in use, etc
logging.info(f"CPU usage : {CpuPercent}%")
logging.info(f"Memory usage : {Mem.percent}%")

CpuUsage.set(CpuPercent)
MemoryUsage.set(Mem.percent)


Columns = ['unit_number', 'time', 'operational_setting_1', 'operations_setting_2', 'operational_setting_3'] + [f'_sensor_{i}' for i in range(1,22)]
TrainData = pd.read_csv("train_FD001.txt", sep = r"\s+", header = None, names=Columns)
TestData = pd.read_csv("test_FD001.txt", sep = r"\s+", header = None, names=Columns)

SensorColumns = [col for col in TrainData.columns if 'sensor' in col]

# Initialize the model
model = IsolationForest(n_estimators=100,contamination=0.05, random_state=42)

start = time.time()
model.fit(TrainData[SensorColumns])
TrainPreds=model.predict(TrainData[SensorColumns])
end= time.time()

logging.info(f"Inference time {end-start:.2f} seconds")
TestPreds=model.predict(TestData[SensorColumns]) 

# Add anomalies to the dataset
TrainData['anomaly'] = TrainPreds
TestData['anomaly'] = TestPreds

# Filter anomalies
TrainAnomaly=TrainData[TrainData['anomaly'] == -1]
TestAnomaly=TestData[TestData['anomaly'] == -1]

# Log stats
logging.info(f"Total anomalies in training data detected : {TrainAnomaly.sum()}")
logging.info(f"Total anomalies in test data detected : {TestAnomaly.sum()}")

AnomalyCountTrain.set(int(TrainAnomaly.sum().sum()))
AnomalyCountTest.set(int(TestAnomaly.sum().sum()))

for col in SensorColumns:
    plt.figure(figsize=(8,4))
    plt.plot(TrainData.index, TrainData[col], label="Sensor values")
    plt.scatter(TrainAnomaly.index, TrainAnomaly[col], color='red', label='Anomalies')
    plt.title(f"Isolation Forest - {col}")
    plt.legend()
    plt.savefig(f"output/plots/anomaly_plot_train{col}.png")  # save to a folder inside container
    plt.close()


for col in SensorColumns:
    plt.figure(figsize=(8,4))
    plt.plot(TestData.index, TestData[col], label="Sensor values")
    plt.scatter(TestAnomaly.index, TestAnomaly[col], color='red', label='Anomalies')
    plt.title(f"Isolation Forest - {col}")
    plt.legend()    
    plt.savefig(f"output/plots/anomaly_plot_test{col}.png")  # save to a folder inside container
    plt.close()

TrainAnomaly.to_csv('output/TrainAnomalyResults.csv')
TestAnomaly.to_csv('output/TestAnomalyResults.csv')

print("Anomaly Detection complete")
logging.info("Anomaly Detection complete")

logging.shutdown()


while True:
    time.sleep(5)