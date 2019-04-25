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
import warnings
import itertools
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import statsmodels.api as sm


consumer = KafkaConsumer(
    "collectd",
    # group_id='arima',
    auto_offset_reset="earliest",
    bootstrap_servers=["152.46.17.159:9092"],
    consumer_timeout_ms=10000,
)
memory_redis = []
time_stamp = []
for msg in consumer:
    value = msg.value
    result = json.loads(value.decode("utf8"))
    if result[0]["type"] == "memory" and result[0]["plugin"] == "redis":
        if result[0]["values"][0]:
            if not math.isnan(float(result[0]["values"][0])):
                memory_redis.append(result[0]["values"][0])
                time_stamp.append(result[0]["time"])

consumer.close()
memory_redis=memory_redis[len(memory_redis)-1000:]
time_stamp=time_stamp[len(time_stamp)-1000:]

def predict_arima(df):


    ############################################
    trace = go.Scatter(
        x=df.index, 
        y=df["memory_used"],
        mode = 'markers'
    )
    data = [trace]
    plot(data, filename="memory-used-overtime")
    # pm.plot_pacf(df)


    # Define the p, d and q parameters to take any value between 0 and 2
    p = d = q = range(0, 2)

    # Generate all different combinations of p, q and q triplets
    pdq = list(itertools.product(p, d, q))

    # Generate all different combinations of seasonal p, q and q triplets
    seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]

    print('Examples of parameter combinations for Seasonal ARIMA...')
    print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[1]))
    print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[2]))
    print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[3]))
    print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[4]))

    warnings.filterwarnings("ignore") # specify to ignore warning messages

    for param in pdq:
        for param_seasonal in seasonal_pdq:
            try:
                mod = sm.tsa.statespace.SARIMAX(d,
                                                order=param,
                                                seasonal_order=param_seasonal,
                                                enforce_stationarity=False,
                                                enforce_invertibility=False)

                results = mod.fit()

                print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
            except:
                continue
    mod = sm.tsa.statespace.SARIMAX(df,
                                order=(1, 1, 0),
                                seasonal_order=(0, 1, 0, 12),
                                enforce_stationarity=True,
                                enforce_invertibility=False)

    results = mod.fit()

    print(results.summary().tables[1])
    results.plot_diagnostics(figsize=(15, 12))
    plt.show()

    pred = results.get_prediction(start=pd.to_datetime('1998-01-01'), dynamic=False)
    pred_ci = pred.conf_int()
    ax = df['1990':].plot(label='observed')
    pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7)

    ax.fill_between(pred_ci.index,
                    pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.2)

    ax.set_xlabel('Date')
    ax.set_ylabel('CO2 Levels')
    plt.legend()

    plt.show()

df = pd.DataFrame()
df["time_stamp"] = time_stamp
df["time_stamp"] = pd.to_datetime(df["time_stamp"], unit='s')
df["memory_used"] = memory_redis
df.set_index("time_stamp",inplace=True)
predict_arima(df)
