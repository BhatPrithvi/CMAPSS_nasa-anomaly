# The data are provided as a zip-compressed text file with 26 columns of numbers, separated by spaces. Each row is a snapshot of data taken during a single operational cycle, each column is a different variable. The columns correspond to:
# 1)	unit number
# 2)	time, in cycles
# 3)	operational setting 1
# 4)	operational setting 2
# 5)	operational setting 3
# 6)	sensor measurement  1
# 7)	sensor measurement  2
#...
# 26)	sensor measurement  26


import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import scipy.stats as stats


columns = ['unit_number', 'time', 'operational_setting_1', 'operations_setting_2', 'operational_setting_3'] + [f'_sensor_{i}' for i in range(1,22)]
TrainData = pd.read_csv("train_FD001.txt", sep = r"\s+", header = None, names=columns)

#Analyse the dataset
#print(TrainData.isna().sum())
#print(TrainData.isnull().sum())
#print(TrainData.head())

#Normalize sensor readings
scaler = StandardScaler()
SensorColumns = [col for col in TrainData.columns if 'sensor' in col]

#The distribution before normalization
#print(TrainData[SensorColumns].mean())
#print(TrainData[SensorColumns].std())

# Fit and transform
TrainData.loc[:, SensorColumns] = scaler.fit_transform(TrainData[SensorColumns])

#Check the distribution
for col in SensorColumns:
    data = TrainData[col]

    # Histogram
    plt.hist(data, bins=30, density=True, alpha=0.6)
    # stats.probplot(data, dist="norm", plot=plt)  # Q-Q plot
    plt.show()

# Verify mean ~0 and std ~1
#print(TrainData[SensorColumns].mean())
#print(TrainData[SensorColumns].std())
#print(TrainData.head())


#Z-score anamolies detection
ZScores = np.abs((TrainData[SensorColumns]-TrainData[SensorColumns].mean())/TrainData[SensorColumns].std())

threshold = 3.0  #About 99.7% lie within ±3 standard deviations.i.e std 1:2:3::68%:95%:99.7%

for col in SensorColumns:
    Anomalies = TrainData[ZScores[col] > threshold]
    print(f"{col}: {len(Anomalies)} anomalies")
    
    plt.figure(figsize=(8,4))
    plt.plot(TrainData.index, TrainData[col], label="Sensor values", alpha=0.7)
    plt.scatter(Anomalies.index, Anomalies[col], color="red", label="Anomalies", zorder=5)
    plt.title(f"Anomalies in {col}")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.legend()
    plt.show()



#Anamoly detection in test data
#  

