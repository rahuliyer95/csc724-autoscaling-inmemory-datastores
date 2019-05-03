# CSC 724: Auto-Scaling In-Memory Data Stores

This project includes the different modules to demonstrate our work on auto-scaling Redis nodes based on its workload.

## Infrastructure Setup

To setup the infrastructure follow the instructions inside the [vcl-setup](./vcl-setup), [redis-docker](./redis-docker), [scale-node-docker](./scale-node-docker), [workload-docker](./workload-docker) folders.

To install the prediction engine follow the instructions inside the [prediction](./prediction) folder.

The current system only supports [Azure](https://azure.com), so you need azure credentials for things to work properly.

## Prediction Module
The prediction module consists of two models:
1. ARIMA ([Click here](https://github.com/rahuliyer95/csc724-autoscaling-inmemory-datastores/tree/master/prediction/arima) to see the code)
2. RNN ([Click here](https://github.com/rahuliyer95/csc724-autoscaling-inmemory-datastores/tree/master/prediction/rnn) to see the code)

Folder structure (Details only about important files):

### Inside [prediction folder](https://github.com/rahuliyer95/csc724-autoscaling-inmemory-datastores/tree/master/prediction)
    .
    ├── rnn                  # Python code files of RNN
    ├── arima                # Python code files of ARIMA
    ├── rnn_model.sav        # Pre-trained model used in online-phase
    ├── predictionEngine.py  # Main python file which calls consumer for streaming data and calls RNN and ARIMA to predict
    ├── consumer.py          # Fetches data from Kafka and gives the response to predictionEngine
    ├── forecast.pickle      # A trained ARIMA model saved using pickle
    └── README.md

#### Inside [RNN](https://github.com/rahuliyer95/csc724-autoscaling-inmemory-datastores/tree/master/prediction/rnn) folder
    .
    ├── multivariate_rnn-offline.py         # Offline phase of RNN which trains the model
    ├── multivariate_rnn.py	                # Considers latency,memory and CPU for prediction
    ├── online_rnn.py                       # Python file that runs during the online-phase(integrated with system)
    └── README.md                           # Code described in detail for RNN

#### Inside [ARIMA](https://github.com/rahuliyer95/csc724-autoscaling-inmemory-datastores/tree/master/prediction/arima) folder
     .
    ├── auto_arima.py                       # 
    ├── arima.py	                          # 
    ├── stat.py                             # 
    └── README.md                           # Code described in detail for ARIMA

