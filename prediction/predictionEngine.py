from arima import arima
import producer
import threading
from threading import Timer

def predict():
    arima_result = arima.arima_model()
    # RNN()

    send_data_producer(arima_result)

def send_data_producer(result):
    producer.producer(result)

predict()
# threading.Timer(60*15,predict).start()