from kafka import KafkaConsumer

def consume():
    consumer = KafkaConsumer(
    "collectd",
    group_id='arima',
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    bootstrap_servers=["152.46.17.159:9092"],
    consumer_timeout_ms=10000,
    )
    memory_redis = []
    time_stamp = []
    memory_host = defaultdict(list)
    timestamp_host = defaultdict(list)

    for msg in consumer:
        value = msg.value
        result = json.loads(value.decode("utf8"))
        if result[0]["type"] == "memory" and result[0]["plugin"] == "memory" and  result[0]["type_instance"] == "used":
            if result[0]["values"][0]:
                if not math.isnan(float(result[0]["values"][0])):
                    print(result[0]["host"])
                    print(result[0]["values"][0])
                    try:
                        memory_host[result[0]["host"]].append(result[0]["values"][0])
                        timestamp_host[result[0]["host"]].append(result[0]["time"])
                    except Exception as e:
                        logging.error(e)
                        continue

    for hosts in memory_host.keys():
        print(memory_host[hosts])
            
    for values in itertools.zip_longest(*memory_host.values(),fillvalue=0):
        memory_redis.append(sum(values)/1024)
    for values in itertools.zip_longest(*timestamp_host.values(),fillvalue=0):
        time_stamp.append(max(values))
    consumer.close()
    # memory_redis=memory_redis[max(1000,len(memory_redis)-1000):]
    # time_stamp=time_stamp[max(0,len(time_stamp)-1000):]


    df = pd.DataFrame()
    df["time_stamp"] = time_stamp
    df["time_stamp"] = pd.to_datetime(df["time_stamp"], unit='s', utc=True)
    df["memory_used"] = memory_redis
    x = pd.Series(df["memory_used"])


    df.set_index("time_stamp",inplace=True)
    
    return df