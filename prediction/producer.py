import json
from asyncio import log

from kafka import KafkaProducer
from kafka.errors import KafkaError


def producer(result):
    kafka_producer = KafkaProducer(bootstrap_servers='152.46.17.159:9092',value_serializer=lambda v: json.dumps(v).encode('utf-8'),api_version=(0,10,1))
    future = kafka_producer.send('prediction',result)
    kafka_producer.flush()
    try:
        record_metadata = future.get(timeout=10)
    except KafkaError:
        # Decide what to do if produce request failed...
        log.exception()
        pass
    return
