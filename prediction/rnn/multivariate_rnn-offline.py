import pickle
from collections import defaultdict
from kafka import KafkaConsumer, KafkaProducer
import json
import csv
import math
from math import sqrt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pip.utils import logging
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from keras import Sequential
from keras.layers import Dense, LSTM
import itertools
status='None'
#def rnn():
consumer = KafkaConsumer('collectd', auto_offset_reset='earliest',group_id='rnn3', enable_auto_commit=True,
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
    result = json.loads(value.decode("utf8"))
    if result[0]["type"] == "memory" and result[0]["plugin"] == "memory" and result[0]["type_instance"] == "used":
        if result[0]["values"][0]:
            if not math.isnan(float(result[0]["values"][0])):

                print(value)
                try:
                    memory_host[result[0]["host"]].append(result[0]["values"][0] / 1024 * 1024)
                    timestamp_host[result[0]["host"]].append(result[0]["time"])
                except Exception as e:
                    logging.error(e)
                    continue

for hosts in memory_host.keys():
    print(memory_host[hosts])


for values in itertools.zip_longest(*memory_host.values(),fillvalue=0):
    memory_redis.append(sum(values) / 1024)
for values in itertools.zip_longest(*timestamp_host.values(),fillvalue=0):
    time_stamp.append(max(values))

consumer.close()

memory_redis=memory_redis[max(0,len(memory_redis)-1000):]
time_stamp=time_stamp[max(0,len(time_stamp)-1000):]

print(memory_redis,"this is redis memory")

#print("Number of nodes in cluster is ",len(nodes_count.keys()))
with open('collectd-data-multivariate.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(zip(time_stamp, memory_redis))




try:
    redis_data = pd.read_csv("collectd-data-multivariate.csv")
    input_feature= redis_data.iloc[:,[0,1]].values
    input_data = input_feature
    sc= MinMaxScaler(feature_range=(0,1))
    input_data[:,0:2] = sc.fit_transform(input_feature[:,:])

    lookback = 10

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
    model.fit(X, y, epochs=5, batch_size=32)
    filename = 'rnn_model.sav'
    pickle.dump(model, open(filename, 'wb'))


    loaded_model = pickle.load(open('rnn_model.sav', 'rb'))
    predicted_value = loaded_model.predict(X_test)
    avg_value = 0
    if (len(predicted_value) > 0):
        avg_value = sum(predicted_value) / len(predicted_value)
        avg_value[0]=avg_value*100000000
    if ((avg_value[0] / 1024) > 0.70 * (len(memory_host.keys()) * 1024 * 1024)):
        status = 'up'
    elif ((avg_value[0] / 1024) < 0.30 * (len(memory_host.keys())) * 1024 * 1024):
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

    print("Predicted Value", predicted_value)
    print("Current Value", X_test)

    rms = sqrt(mean_squared_error(Y_test,predicted))
    print(predicted_value,"this is predicted value")
    print(Y_test,"this is actual value")
    plt.plot(predicted_value, color= 'red',label='predicted')
    print("this is test_size",test_size)
    print("this is lookback",lookback)
    print("type of input data",type(input_data))
    plt.plot(Y_test, color='green',label='actual')
    plt.title("Memory based prediction")
    plt.xlabel("Time")
    plt.ylabel("Memory")
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.show()

    print(autoScale)

except:
    autoScale = json.dumps({
        'status_of_rnn': 'no',
        'rnn_load': 0
    })















