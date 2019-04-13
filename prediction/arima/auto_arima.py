from kafka import KafkaConsumer, KafkaProducer
import json
import math
import plotly
import plotly.plotly as py
import matplotlib.pyplot as plt
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot_mpl, iplot, plot
import plotly.graph_objs as go
import cufflinks as cf
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.model_selection import train_test_split
import pandas as pd
from pmdarima import auto_arima
from pmdarima.arima import ADFTest,ARIMA, CHTest
from pmdarima.utils import c, diff
import pmdarima as pm
from pmdarima.arima.utils import ndiffs, nsdiffs
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error
from collections import defaultdict


consumer = KafkaConsumer(
"collectd",
# group_id='arima1',
auto_offset_reset="earliest",
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
                memory_host[result[0]["host"]].append(result[0]["values"][0])
                timestamp_host[result[0]["host"]].append(result[0]["time"])


for values in zip(*memory_host.values()):
    memory_redis.append(sum(values))
for values in zip(*timestamp_host.values()):
    time_stamp.append(sum(values)/(len(values)))

consumer.close()
memory_redis=memory_redis[max(0,len(memory_redis)-1000):]
time_stamp=time_stamp[max(0,len(time_stamp)-1000):]


def predict_arima(df):


    ############################################
    trace = go.Scatter(
        x=df.index, 
        y=df["memory_used"],
        mode = 'lines+markers'
    )
    data = [trace]
    plot(data, filename="memory-used-overtime")
    # pm.plot_pacf(df)
    # pm.plot_acf(df)

    adf_test=ADFTest(alpha=0.05)
    p_val, should_diff = adf_test.is_stationary(df["memory_used"])
    ch_test=CHTest(12)
    print(ch_test.estimate_seasonal_differencing_term(df))
    
    nd = ndiffs(df, test='adf')
    print(nd)
    nsd = nsdiffs(df,12)
    print(nd)
        
    train, test = train_test_split(df,shuffle=False, test_size=0.3)
    print(len(train)    )
    stepwise_model = auto_arima(train, start_p=0, start_q=0,
                           max_p=4, max_q=4, m=40,
                           start_P=0, start_Q=0,
                           seasonal=True,
                           d=0, max_d=2, D=1, max_D=2, trace=True,
                           error_action='ignore',  
                           suppress_warnings=True, 
                           stepwise=True)       
    print(stepwise_model.aic())

    stepwise_model.fit(train)

    future_forecast = stepwise_model.predict(n_periods=len(test))
    future_forecast = pd.DataFrame(future_forecast,index = test.index,columns=['prediction'])
    print(future_forecast)
    res=pd.concat([df,future_forecast],axis=1)
    print(res)
    trace1 = go.Scatter(x=res.index, y=res["prediction"],name="Prediction", mode='lines+markers')
    trace2 = go.Scatter(x=res.index, y=res["memory_used"],name="Test data", mode='lines+markers')
    data=[trace1,trace2]
    
    plot(data, filename="prediction")



df = pd.DataFrame()
df["time_stamp"] = time_stamp
df["time_stamp"] = pd.to_datetime(df["time_stamp"], unit='s', utc=True)
df["memory_used"] = memory_redis
x = pd.Series(df["memory_used"])


df.set_index("time_stamp",inplace=True)
predict_arima(df)