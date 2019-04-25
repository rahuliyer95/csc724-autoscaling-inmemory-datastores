from arima import arima
import producer
import threading
import json
from threading import Timer
import time
import sys
from keras.backend import rnn
from rnn import online_rnn
import consumer
def predict(df,memory_host):
    print(df)
    print("**********************ARIMA MODEL*************************")
    arima_result= arima.arima_model(df,memory_host)
    print("************************RNN*******************************")
    print(memory_host)
    rnn_result,rnn_rmse=online_rnn.rnn(df,memory_host)
    
    arima_data=json.loads(arima_result)
    rnn_data=json.loads(rnn_result)
    rnn_status=rnn_data["scale"]

    arima_data=json.loads(arima_result)
    arima_status=arima_data['scale']
    # arima_status='no'
    if(arima_status==rnn_status):
        autoScaleData = {
            'peak_value': arima_data['peak_value'],
            'average_value': arima_data['average_value'],
            'nodes': arima_data['nodes'],
            'scale': arima_data['scale']
        }

    else:
        autoScaleData ={
            'peak_value': rnn_data['peak_value'],
            'average_value': rnn_data['average_value'],
            'nodes': rnn_data['nodes'],
            'scale': rnn_data['scale']
        }

    print("********************************************")
    print("The autoscale message sent to Scaling engine:")
    print(json.dumps(autoScaleData))
    return send_data_producer(autoScaleData)

def send_data_producer(result):
   return producer.producer(result)


while True:
    df,memory_host=consumer.consume()
    predict(df,memory_host)
    for remaining in range(420, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)

    sys.stdout.write("\rStarting Prediction Engine ......... \n")
