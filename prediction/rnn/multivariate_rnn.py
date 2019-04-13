from math import sqrt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from keras import Sequential
from keras.layers import Dense, LSTM

from kafka import KafkaConsumer, KafkaProducer
import json
import csv
from math import sqrt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from keras import Sequential
from keras.layers import Dense, LSTM

consumer = KafkaConsumer('collectd', auto_offset_reset='earliest',
                         bootstrap_servers=['152.46.17.159:9092'], consumer_timeout_ms=10000)
memory_redis = []
time=[]
cpu=[]
latency=[]
nodes_count=dict()
for msg in consumer:
    value = msg.value
    result = json.loads(value.decode('utf8'))

    if result[0]["type"] == "memory" and result[0]["plugin"] == "redis":
        print(result)
        memory_redis.append(result[0]["values"][0])
        time.append(result[0]['time'])
    if result[0]['host'] not in nodes_count:
        nodes_count[result[0]['host']]=1


    if result[0]["type"]== "disk_io_time" and result[0]['plugin_instance'] == 'sda' and not result[0]['values'][0]==None:

        latency.append(result[0]['values'][0])

    if result[0]["type"]== "cpu" and result[0]["plugin"] == "cpu" and result[0]['type_instance']=="system" and not result[0]['values'][0]==None:
        cpu.append(result[0]['values'][0])


memory_redis=memory_redis[len(memory_redis)-1000:]
latency=latency[len(latency)-1000:]
cpu=cpu[len(cpu)-1000:]
print("Number of nodes in cluster is ",len(nodes_count.keys()))
with open('collectd-data-multivariate.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(zip(latency, memory_redis,cpu))
consumer.close()



redis_data = pd.read_csv("collectd-data-multivariate.csv")
input_feature= redis_data.iloc[:,[0,1]].values
input_data = input_feature
sc= MinMaxScaler(feature_range=(0,1))
input_data[:,0:2] = sc.fit_transform(input_feature[:,:])

lookback = 300

test_size = int(.3 * len(redis_data))
X = []
y = []
for i in range(len(redis_data) - lookback - 1):
    t = []
    for j in range(0, lookback):
        t.append(input_data[[(i + j)], :])
    X.append(t)
    y.append(input_data[i + lookback, 1])

X, y= np.array(X), np.array(y)
X_test = X[:test_size+lookback]
Y_test=y[:test_size+lookback]
X = X.reshape(X.shape[0],lookback, 2)
X_test = X_test.reshape(X_test.shape[0],lookback, 2)

model = Sequential()
model.add(LSTM(units=30, return_sequences= True, input_shape=(X.shape[1],2)))
model.add(LSTM(units=30, return_sequences=True))
model.add(LSTM(units=30))
model.add(Dense(units=1))
print(model.summary())
model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X, y, epochs=50, batch_size=32)
predicted_value= model.predict(X_test)
avg_value=sum(predicted_value)/len(predicted_value)
if(avg_value>0.70*(len(nodes_count.keys()))*8000):
    status='ScaleUp'
elif(avg_value<0.70*(len(nodes_count.keys()))*1000000):
    status='ScaleDown'
else:
    status='Nothing'

predicted=[]
i=0
while i < len(predicted_value):
    predicted.append(predicted_value[i][0])
    i += 1




rms = sqrt(mean_squared_error(Y_test,predicted))
print(rms)
plt.plot(predicted_value, color= 'red',label='predicted')
plt.plot(input_data[lookback:test_size+(2*lookback),1], color='green',label='actual')
plt.title("Memory based prediction")
plt.xlabel("Time")
plt.ylabel("Memory")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.show()
















