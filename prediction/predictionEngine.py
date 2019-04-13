from arima import arima
import threading
from threading import Timer

def predict():
    arima.ARIMA()
    # RNN()
    average_load=80
    peak_load=90
    scale="up"
    node=3
    send_data_producer(average_load,peak_load,scale,node)

def send_data_producer():
    producer(average_load,peak_load,scale,node)

predict()
# threading.Timer(60*15,predict).start()