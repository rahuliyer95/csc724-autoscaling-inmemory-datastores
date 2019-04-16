from arima import arima
import producer
import threading
from threading import Timer

def predict():
    arima_result = arima.arima_model()
    print(arima_result)
    # RNN()

    # send_data_producer(arima_result)

def send_data_producer(result):
    producer.producer(result)


while True:
    predict()
    time.sleep(15*60)