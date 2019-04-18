from arima import arima
import producer
import threading
import json
from threading import Timer
from rnn import multivariate_rnn
import time
def predict():
    arima_result = arima.arima_model()
    rnn_result=multivariate_rnn.rnn()

    rnn_data=json.loads(rnn_result)
    rnn_status=rnn_data["status_of_rnn"]

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
            'peak_value': arima_data['peak_value'],
            'average_value': arima_data['average_value'],
            'nodes': arima_data['nodes'],
            'scale': rnn_data['status_of_rnn']
        }
    print(json.dumps(autoScaleData))
    send_data_producer(autoScaleData)

def send_data_producer(result):
    producer.producer(result)


while True:
    predict()
    time.sleep(15*60)
