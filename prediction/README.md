### Prediction Engine
We have implemented two models: ARIMA Model and Recurrent Neural Network

#### Setup
- Install requirements using Pipfile
```sh
# python install -r Pipfile
```
- Setup Prediction Service
```sh
# cp prediction.service /etc/systemd/system/
```
- Setup KafkaConsumer and KafkaProducer:

In `producer.py` and `consumer.py`, enter the IP address of the bootstrap server where Kafka service is running

- Start the prediction engine
```sh
# systemctl daemon-reload
# systemctl start prediction.service
```
- Serve the output files using python http server
#### Firewall

To allow services through firewall iptables setup needs to be done. Use the following commands to add iptables exception (run as root)

```sh
iptables -I INPUT -p TCP -s 0.0.0.0/0 --dport 8000 -j ACCEPT # python simple http
```
Run python http server
```sh
# cd outputs
# python -m http.server -b 0.0.0.0
```
The outputs can be viewed at http://IP_Address:8000

#### Prediction & Scaling Policy
Prediction policy:
```python
if (average)>0.70*(len(memory_host.keys())*1024):
    status='up'
elif (average)<0.30*(len(memory_host.keys()))*1024:
    status='down'
else:
    status='no'
```

Scaling Policy:

| ARIMA   |      RNN      |  AutoScale |
|----------|:-------------:|------:|
| UP       |  NO           | UP    |
| NO       |          UP   |    UP |
| DOWN     | NO            | NO    |
|NO        |DOWN           |  NO   |
