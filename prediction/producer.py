import json
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='152.46.17.159:9092',value_serializer=lambda v: json.dumps(v).encode('utf-8'),api_version=(2,1,1))
def producer(average_load,peak_load,scale,node):

    future = producer.send('prediction',{
        'average_load':80,
        'peak_load':90,
        'scale':"up",
        'nodes':3
    })
    producer.flush()
    try:
        record_metadata = future.get(timeout=10)
    except KafkaError:
        # Decide what to do if produce request failed...
        log.exception()
        pass
