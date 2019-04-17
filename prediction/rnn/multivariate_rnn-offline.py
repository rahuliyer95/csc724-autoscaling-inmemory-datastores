import pickle
from collections import defaultdict
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
status='None'
#def rnn():
consumer = KafkaConsumer('collectd', auto_offset_reset='earliest',group_id='rnn1', enable_auto_commit=True,
                         bootstrap_servers=['152.46.17.159:9092'], consumer_timeout_ms=10000)
memory_redis = []
time=[]
cpu=[]
latency=[]
nodes_count=dict()
memory_hashmap=dict()
cpu_hashmap=dict()
latency_hashmap=dict()
memory_host=defaultdict(list)
timestamp_host=defaultdict(list)
time_stamp=[]

for msg in consumer:
    value = msg.value
    result = json.loads(value.decode('utf8'))

    if result[0]["type"] == "memory" and result[0]["plugin"] == "memory" and result[0]["type_instance"] == "used":
        print(result)
        memory_redis.append(result[0]["values"][0])
        if(result[0]['time'] not in memory_hashmap):
            memory_hashmap[result[0]['time']]=result[0]["values"][0]
        else:
            memory_hashmap[result[0]['time']]=memory_hashmap.get(result[0]['time'])+result[0]["values"][0]
        time.append(result[0]['time'])

    if result[0]['host'] not in nodes_count:
        nodes_count[result[0]['host']]=1


    if result[0]["type"]== "disk_io_time" and result[0]['plugin_instance'] == 'sda' and not result[0]['values'][0]==None:
        if (result[0]['time'] not in latency_hashmap):
            latency_hashmap[result[0]['time']] = result[0]["values"][0]
        else:
            latency_hashmap[result[0]['time']] = latency_hashmap.get(result[0]['time']) + result[0]["values"][0]

    if result[0]["type"]== "cpu" and result[0]["plugin"] == "cpu" and result[0]['type_instance']=="system" and not result[0]['values'][0]==None:
        if (result[0]['time'] not in cpu_hashmap):
            cpu_hashmap[result[0]['time']] = result[0]["values"][0]
        else:
            cpu_hashmap[result[0]['time']] = cpu_hashmap.get(result[0]['time']) + result[0]["values"][0]


time_stamp=time_stamp[max(0,len(time_stamp)-1000):]

memory_redis=list(memory_hashmap.values())
memory_redis=memory_redis[max(0,len(memory_redis)-1000):]


latency=[x / len(nodes_count.keys()) for x in list(latency_hashmap.values())]
latency=latency[len(latency)-1000:]




cpu=[y / len(nodes_count.keys()) for y in list(cpu_hashmap.values())]
cpu=cpu[max(0,len(cpu)-1000):]


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

lookback = 100

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
model.fit(X, y, epochs=10, batch_size=32)
filename = 'rnn_model.sav'
pickle.dump(model, open(filename, 'wb'))


loaded_model = pickle.load(open('rnn_model.sav', 'rb'))
predicted_value = loaded_model.predict(X_test)
print(len(predicted_value), "this is length of predicted value")
print("sum of predicted value", sum(predicted_value))
avg_value = 0
if (len(predicted_value) > 0):
    avg_value = sum(predicted_value) / len(predicted_value)

if ((avg_value[0] / 1024) > 0.70 * (len(nodes_count.keys()) * 1024 * 1024)):
    status = 'up'
elif ((avg_value[0] / 1024) < 0.30 * (len(nodes_count.keys())) * 1024 * 1024):
    status = 'down'
else:
    status = 'no'
print(status, "this is the status")
predicted = []
i = 0

while i < len(predicted_value):
    predicted.append(predicted_value[i][0])
    i += 1
autoScale = json.dumps({
    'status_of_rnn': status,
    'rnn_load': float(avg_value[0]/1024*1024)
})



rms = sqrt(mean_squared_error(Y_test,predicted))
# print(predicted_value,"this is predicted value")
# print(Y_test,"this is actual value")
# plt.plot(predicted_value, color= 'red',label='predicted')
# plt.plot(input_data[lookback:test_size+(2*lookback),1], color='green',label='actual')
# #plt.plot(Y_test, color='green',label='actual')
# plt.title("Memory based prediction")
# plt.xlabel("Time")
# plt.ylabel("Memory")
# plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
# plt.show()

print(autoScale)














