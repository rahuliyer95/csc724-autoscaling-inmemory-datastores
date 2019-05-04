## RNN Model
This model presently has two phases:
1. Online Phase: Uses pre-trained model which was trained in offline phase.
2. Offline Phase: Training the model with 3 days data

File [online_rnn.py](https://github.com/rahuliyer95/csc724-autoscaling-inmemory-datastores/blob/master/prediction/rnn/online_rnn.py) is the file that runs in an integrated system.
File [multivariate_rnn-offline.py](https://github.com/rahuliyer95/csc724-autoscaling-inmemory-datastores/blob/master/prediction/rnn/multivariate_rnn-offline.py) is the offline trained model

Here is the construction of the model:
A small code snippet:
```
    model = Sequential()
    model.add(LSTM(units=30, return_sequences= True, input_shape=(X.shape[1],2)))
    model.add(LSTM(units=30, return_sequences=True))
    model.add(LSTM(units=30))
    model.add(Dense(units=1))
    print(model.summary())
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X, y, epochs=100, batch_size=32)
```

Decision Code:

```
        if((average)>0.70*(len(memory_host.keys())*1024)):
            status='up'
        elif((average)<0.30*(len(memory_host.keys()))*1024):
            status='down'
        else:
            status='no'
```

## To only run rnn:

Go to directory /rnn:

Run online_rnn.py
