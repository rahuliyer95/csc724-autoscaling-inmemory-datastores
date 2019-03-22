from kafka import KafkaConsumer, KafkaProducer
import json
import plotly.plotly as py
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot_mpl, iplot, plot
import plotly.graph_objs as go
import cufflinks as cf
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.model_selection import train_test_split
import pandas as pd
from matplotlib import pyplot
from pyramid.arima import auto_arima

consumer = KafkaConsumer(
    "collectd",
    auto_offset_reset="earliest",
    bootstrap_servers=["152.46.17.159:9092"],
    consumer_timeout_ms=10000,
)
memory_redis = []
time_stamp = []
for msg in consumer:
    value = msg.value
    result = json.loads(value.decode("utf8"))
    if result[0]["type"] == "cpu" and result[0]["plugin"] == "cpu":
        if(result[0]["values"][0]):
            memory_redis.append(result[0]["values"][0])
            time_stamp.append(result[0]["time"])
    # if len(memory_redis) == 1000:
    #     break
consumer.close()
memory_redis=memory_redis[len(memory_redis)-1000:]
time_stamp=time_stamp[len(time_stamp)-1000:]

def predict_arima(df):
    trace = go.Scatter(x=df.index, y=df["memory_used"])
    data = [trace]
    plot(data, filename="memory-used-overtime")
    decomposition = seasonal_decompose(df, freq=5, model="multiplicative")
    print(decomposition.seasonal)
    print(decomposition.trend)
    print(decomposition.resid)
    trace1 = go.Scatter(
    x = df.index,y = decomposition.trend,
    name = 'Trend',mode='lines'
    )
    trace2 = go.Scatter(
        x = df.index,y = decomposition.seasonal,
        name = 'Seasonal',mode='lines'
    )
    trace3 = go.Scatter(
        x = df.index,y = decomposition.resid,
        name = 'Residual',mode='lines'
    )

    data=[trace1]
    plot(data,filename='seasonal_decomposition')

    stepwise_model = auto_arima(
        df, start_p=1, start_q=1,
                           max_p=3, max_q=3, m=12,
                           start_P=0, seasonal=True,
                           d=1, D=1, trace=True,
                           error_action='ignore',  
                           suppress_warnings=True, 
                           stepwise=True
    )
    print(stepwise_model.aic())

    train, test = train_test_split(df,shuffle=False, test_size=0.2)
    print(train.head())
    stepwise_model.fit(train)

    future_forecast = stepwise_model.predict(n_periods=int(len(df["memory_used"])*0.2))


    future_forecast = pd.DataFrame(future_forecast,index = test.index,columns=["prediction"])
    print(future_forecast.head())

    
    res=pd.concat([test,future_forecast],axis=1)
    print(res)
    trace1 = go.Scatter(x=res.index, y=res["prediction"],name="Prediction", mode='lines')
    trace2 = go.Scatter(x=res.index, y=res["memory_used"],name="Test data", mode='lines')
    data=[trace1,trace2]
    plot(data, filename="prediction")
 



df = pd.DataFrame()
df["time_stamp"] = time_stamp
df["time_stamp"] = pd.to_datetime(df["time_stamp"],unit='ms')
df["memory_used"] = memory_redis
df.set_index("time_stamp",inplace=True)
print(df)
predict_arima(df)
