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

def arima():

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
                    # memory_redis.append(result[0]["values"][0])
                    timestamp_host[result[0]["host"]].append(result[0]["time"])
    print(memory_host.keys())


    for values in zip(*memory_host.values()):
        print(values)
        memory_redis.append(sum(values))
    for values in zip(*timestamp_host.values()):
        print(values)
        time_stamp.append(sum(values)/(len(values)))

    consumer.close()
    memory_redis=memory_redis[max(0,len(memory_redis)-200):]
    time_stamp=time_stamp[max(0,len(time_stamp)-200):]
    df = pd.DataFrame()
    df["time_stamp"] = time_stamp
    df["time_stamp"] = pd.to_datetime(df["time_stamp"], unit='s', utc=True)
    df["memory_used"] = memory_redis
    df.set_index("time_stamp",inplace=True)
    print(df)


    trace = go.Scatter(
        x=df.index, 
        y=df["memory_used"],
        mode = 'lines+markers'
    )
    data = [trace]
    plot(data, filename="memory-used-overtime")


    adf_test=ADFTest(alpha=0.05)
    p_val, should_diff = adf_test.is_stationary(df["memory_used"])
    ch_test=CHTest(90)
    print(ch_test.estimate_seasonal_differencing_term(df))
    
    nd = ndiffs(df, test='adf')
    print(nd)
    nsd = nsdiffs(df,12)
    print(nd)

    # x=seasonal_decompose(df, model='multiplicative', filt=None, freq=1, two_sided=True, extrapolate_trend=0)
    train, test = train_test_split(df,shuffle=False, test_size=0.2)

    # res = sm.tsa.ARMA(df, (3, 0)).fit()
    # fig, ax = plt.subplots()
    

    ##########################################
    p=0
    q=0
    d=0
    pdq=[]
    aic=[]

    for p in range(4):
        for d in range(2):
            for q in range(2):
            
                try:
                    stepwise_model = ARIMA(
                        order=(p,d,q),
                        seasonal_order=(0,1,0,90),
                        suppress_warnings=True, 
                        error_action='ignore',
                        scoring='mse'
                    )
                    x=str(p)+" "+str(d)+" "+str(q)
                    print(x)

                    stepwise_model.fit(train)
                    future_forecast = stepwise_model.predict(n_periods=len(test))
                    print(future_forecast)
                    future_forecast = pd.DataFrame(future_forecast,index = test.index,columns=["prediction"])
                    print(test)
                    
                    print(mean_absolute_error(test, future_forecast))

                    
                    res=pd.concat([test,future_forecast],axis=1)

                    trace1 = go.Scatter(x=res.index, y=res["prediction"],name="Prediction", mode='lines')
                    trace3 = go.Scatter(x=res.index, y=res["memory_used"],name="Test", mode='lines')

                    trace2 = go.Scatter(x=df.index, y=df["memory_used"],name="DF data", mode='lines')
                    data=[trace1,trace2,trace3]
                    layout = go.Layout(
                        title=x
                    )
                    fig = go.Figure(data=data, layout=layout)
                    plot(fig, filename="prediction")

                except:
                    continue

    

arima()
"""
# auto_arima
stepwise_model = auto_arima(train, start_p=0, start_q=0,
                           max_p=4, max_q=4, m=60,
                           start_P=0, start_Q=0,
                           seasonal=True,
                           d=0, max_d=2, D=0, max_D=2, trace=True,
                           error_action='ignore',  
                           suppress_warnings=True, 
                           stepwise=True)       
print(stepwise_model.aic())
"""