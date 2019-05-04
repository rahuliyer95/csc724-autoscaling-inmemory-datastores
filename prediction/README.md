### Prediction Engine
We have implemented two models: ARIMA Model and Recurrent Neural Network

#### Setup
- Install requirements using Pipfile
```
# python install -r Pipfile
```
- Setup Prediction Service
```
# cp prediction.service /etc/systemd/system/
```
- Setup KafkaConsumer and KafkaProducer:

In `producer.py` and `consumer.py`, enter the IP address of the bootstrap server where Kafka service is running

- Start the prediction engine
```
# systemctl daemon-reload
# systemctl start prediction.service
```
- Serve the output files using python http server
```
# cd outputs
# python -m http.server -b 0.0.0.0
```
