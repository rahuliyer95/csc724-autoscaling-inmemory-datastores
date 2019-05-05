## ARIMA Models
1. Check stationarity: If a time series has a trend or sea-sonality component, it must be made stationary beforewe can use ARIMA to forecast.
2. Difference: If the time series is not stationary, it needsto be stationarized through differencing. Take the firstdifference, then check for stationarity. Take as manydifferences as it takes. Make sure you check seasonaldifferencing as well.
3. Filter out a validation sample: This will be used tovalidate how accurate our model is. Use train test vali-dation split to achieve this
4. Select AR and MA terms: Use the ACF and PACF todecide whether to include an AR term(s), MA term(s),or both.
5. Build the model: Build the model and set the numberof periods to forecast to N= no of future datapoints


#### Using ARIMA function

Choose ARIMA when manually choosing to select values of p,d,q
```python
stepwise_model = ARIMA(
        order=(p,d,q),
        seasonal_order=(0,nsd,0,12),
        suppress_warnings=True,
        scoring='mse'
        )
```


#### Using autoarima function

Choose AutoARIMA model to automatically select values of p,d,q from a range of values and selecting the set of values with low AIC value

```python
stepwise_model = auto_arima(train, start_p=0, start_q=0,
                     max_p=4, max_q=4, m=12,
                     start_P=0, start_Q=0,
                     seasonal=True,
                     d=0, max_d=2, D=1, max_D=2, trace=True,
                     error_action='ignore',  
                     suppress_warnings=True, 
                     stepwise=True
                 )
```

