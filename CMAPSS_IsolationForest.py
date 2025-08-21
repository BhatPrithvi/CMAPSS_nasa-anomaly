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