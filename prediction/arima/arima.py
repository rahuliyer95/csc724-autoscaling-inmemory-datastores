from kafka import KafkaConsumer, KafkaProducer
import json
import math
import plotly
import plotly.plotly as py
import matplotlib.pyplot as plt
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot_mpl, iplot, plot
import plotly.graph_objs as go
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf,pacf
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
import json
import logging
import itertools
import pickle
import time

current_milli_time = lambda: int(round(time.time() * 1000))
# logging.basicConfig(filename='app.log', level=logging.INFO, filemode='w', format='%(name)s - %(levelname)s - %(message)s')

def getThreshold():
    return 0.7 # set threshold for ACF

def analyze(predict,memory_host):
    logging.info(predict)
    peak_value=max(predict["prediction"])
    average_value=sum(predict["prediction"])/len(predict)
    nodes=len(memory_host.keys())

    if average_value<0:
        average_value=0
    if (average_value)/(nodes*1024*1024) >0.7:
        scale="up"
    elif (average_value)/(nodes*1024*1024) <0.3:
        scale="down"
    else:
        scale="no"
    autoScale= json.dumps({
        'peak_value': peak_value,
        'average_value': average_value,
        'nodes': nodes,
        'scale': scale
    })
    print(autoScale)
    return autoScale


def predict_arima(df):

    time_in=current_milli_time()
    try:
        forecast_in = open("forecast.pickle","rb")
        future_forecast = pickle.load(forecast_in)
        forecast_in.append(df)
        error=[]
        """
        Calculate errors
        """
        if len(df) < len(future_forecast):
            error=df["memory_used"] - future_forecast[:len(df)]["memory_used"]
        elif len(df) > len(future_forecast):
            error=df[0:len(future_forecast)]["memory_used"]- future_forecast["memory_used"]
        else:
            error=df["memory_used"]-future_forecast["memory_used"]
        overestimation=[x for x in error if x<0]
        overestimation=sum(overestimation)/len(overestimation)
        underestimation=[x for x in error if x>=0]
        underestimation=sum(underestimation)/len(underestimation)
        print("UNDERESTIMATION ERROR: "+underestimation)
        print("OVERESTIMATION ERROR: "+overestimation)
        print("Mean Absolute Error in Last iteration "+str(error))
        """
        Overestimation & Underestimation errors
        """



    except Exception as e:
        print("RMSE To be computed")
        # Do Nothing
  
    try:
        pm.plot_pacf(df,show=False).savefig('pacf.png')
        pm.plot_acf(df,show=False).savefig('acf.png')
    except:
        print("Data points insufficient for ACF & PACF")


    try:
        pickle_in = open("arima.pickle","rb")
        arima_data = pickle.load(pickle_in)
        arima_data.append(df)
        #df=arima_data
    except Exception as e:
        arima_data_out = open("arima.pickle","wb")    
        pickle.dump([], arima_data_out)
    arima_data_out = open("arima.pickle","wb")
    pickle.dump(df, arima_data_out)
    arima_data_out.close()
    
    '''
    tests 
    '''
    nd=1
    nsd=1
    try:
        adf_test=ADFTest(alpha=0.05)
        p_val, should_diff = adf_test.is_stationary(df["memory_used"])    

        nd = ndiffs(df, test='adf')
        logging.info(nd)
        nsd = nsdiffs(df,12)
        logging.info(nd)
    except:
        nd=1
        print("Exception on tests")

    ch_test=CHTest(12)
    
    try:
        nsd=ch_test.estimate_seasonal_differencing_term(df)
    except Exception as e:
        print(e)
        logging.error(e)
    

    '''
        ARIMA MODEL
    '''

    '''
        Find p,q dynamically
    '''
    acf_lags=acf(df["memory_used"])
    acf_lags_threshold=[x for x in acf_lags if x>=getThreshold()]
    p=len(acf_lags_threshold) if len(acf_lags_threshold)<=4 else 4

    pacf_lags=pacf(df["memory_used"])
    pacf_lags_threshold=[x for x in pacf_lags if x>=getThreshold()]
    q=len(pacf_lags_threshold) if len(pacf_lags_threshold)<=1 else 1
    d=nd

    train, test = train_test_split(df,shuffle=False, test_size=0.3)

    # If data is seasonal set the values of P,D,Q in seasonal order
    stepwise_model = ARIMA(
        order=(p,d,q),
        seasonal_order=(0,nsd,0,12),
        suppress_warnings=True,
        scoring='mse'
    )
    x=str(p)+" "+str(nd)+" "+str(q)
    print("Model with p="+str(q)+" d="+str(d)+" q="+str(q))

    try:

        stepwise_model.fit(df)
        """ 
          Vary the periods as per the forecasting window 
          n_periods= 30 = 5mins
          n_periods= 60 = 10mins
          n_periods= 90 = 15mins
        """
        future_forecast = stepwise_model.predict(n_periods=len(test))
        future_forecast = pd.DataFrame(future_forecast,index=test.index,columns=["prediction"])

        res=pd.concat([df,future_forecast],axis=1)

        '''
            Save Forecast in Pickle 
        '''
        forecast_out = open("forecast.pickle","wb")
        pickle.dump(future_forecast,forecast_out)
        forecast_out.close()
        
        trace1 = go.Scatter(x=res.index, y=res["prediction"],name="Prediction", mode='lines')
        trace2 = go.Scatter(x=df.index, y=df["memory_used"],name="DF data", mode='lines')
        data=[trace1,trace2]
        layout = go.Layout(
            title=x
        )
        fig = go.Figure(data=data, layout=layout)
        plot(fig, filename="prediction")
        print("Current values")
        print(df)
        print("Predicted Data Points")
        print(future_forecast)
        time_out=current_milli_time()
        print("TIME for RNN(ms):"+str(time_out-time_in))
        return future_forecast
    except Exception as e:
        time_out=current_milli_time()
        print("TIME for RNN(ms):"+str(time_out-time_in))
        print(e)
        return None




def arima_model(df,memory_host):
        
    forecast = predict_arima(df)
    if forecast is None:
        return json.dumps({
        'peak_value': 0,
        'average_value': 0,
        'nodes': 0,
        'scale': "no"
    })
    
    return analyze(forecast,memory_host)

