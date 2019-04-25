import pickle
from collections import defaultdict
from kafka import KafkaConsumer, KafkaProducer
from decimal import Decimal

import json
import csv
import math
import traceback
import sys
from math import sqrt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt1
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
import itertools

from keras import Sequential
from keras.layers import Dense, LSTM
status='None'
def rnn(df,memory_host):

    time=[]
    cpu=[]
    latency=[]
    nodes_count=dict()
    memory_hashmap=dict()
    cpu_hashmap=dict()
    latency_hashmap=dict()
 
    timestamp_host=defaultdict(list)
    time_stamp=[]

    '''
    memory_redis = []
    memory_redis = []
    for msg in consumer:
        value = msg.value
        result = json.loads(value.decode("utf8"))
        if result[0]["type"] == "memory" and result[0]["plugin"] == "redis": # and result[0]["type_instance"] == "used":
            if result[0]["values"][0]:
                if not math.isnan(float(result[0]["values"][0])):

                    print(value)
                    try:
                        memory_host[result[0]["host"]].append(result[0]["values"][0] /( 1024 * 1024))
                        timestamp_host[result[0]["host"]].append(result[0]["time"])
                    except Exception as e:
                        logging.error(e)
                        continue
    max_length=0
    max_length_host=0
    for hosts in memory_host.keys():
        print(memory_host[hosts])
        if(len(memory_host[hosts])>max_length):
            max_length=len(memory_host[hosts])
            max_length_host=hosts

    for values in itertools.zip_longest(*memory_host.values(), fillvalue=0):
        memory_redis.append(sum(values) / 1024)
    for values in timestamp_host[max_length_host]:
        time_stamp.append(values)

    consumer.close()
    '''
    memory_redis=df["memory_used"]
    #time_stamp=df.index
    memory_redis = memory_redis[max(0, len(memory_redis) - 100):]


    with open('collectd-data-multivariate.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(zip(memory_redis,memory_redis))

    avg_value=0
    predicted=[]
    try:
        average=0
        redis_data = pd.read_csv("collectd-data-multivariate.csv")
        input_feature= redis_data.iloc[:,[0,1]].values

        input_data = input_feature
        sc= MinMaxScaler(feature_range=(0,1))
        input_data[:,0:2] = sc.fit_transform(input_feature[:,:])

        lookback = 10

        test_size = int(len(redis_data))
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


        loaded_model = pickle.load(open('rnn_model.sav', 'rb'))

        predicted_value= loaded_model.predict(X_test)
        if (len(predicted_value) > 0):
            average = np.average(predicted_value)
            average=average*(1024*1024)
            #This is in MB
        if((average)>0.70*(len(memory_host.keys())*1024*1024)):
            status='up'
        elif((average)<0.30*(len(memory_host.keys()))*1024*1024):
            status='down'
        else:
            status='no'
        i=0

        while i < len(predicted_value):
            predicted.append(predicted_value[i][0])
            i += 1
        autoScale = json.dumps({
            'nodes': len(memory_host.keys()),
            'peak_value': str(max(predicted)*1024),
            'scale': status,
            'average_value': str(average)
        })

        print("Predicted Value",predicted_value)
        print("Current Value",redis_data)


        rms = sqrt(mean_squared_error(Y_test,predicted))
        print("ROOT MEAN SQUARE ERROR"+str(rms))
        plt1.plot(predicted_value, color= 'red',label='predicted')

        plt1.plot(input_data[lookback:test_size+(2*lookback),1], color='green',label='actual')
        plt1.title("Memory based prediction")
        plt1.xlabel("Time")
        plt1.ylabel("Memory")
        plt1.legend(bbox_to_anchor=(2.05, 1), loc=2, borderaxespad=0.)
        plt1.savefig('Predictio_rnn.png')
        print(autoScale)
        return autoScale,rms*100
    except Exception as e:
        exc_info = sys.exc_info()
        autoScale = json.dumps({
            'average_value':0,
            'peak_value':0,
            'scale': 'no',
            'nodes': len(memory_host.keys()),
        })
        print(traceback.print_exception(*exc_info))
        return autoScale,0















