# coding=utf-8
# Copyright 2020 Google LLC

'''
USAGE:
anomaly_detection_model.py --training_data './data/game_event_logs.csv' --epochs 10 --batch_size 10 --validation_split 0.05 --model_threshold 0.275 --model_filepath ./models/

TODO:
    - Refactor for tfx pipeline
    - Add parameterization / args
    - Add feature engineering to enhance model
    - Add new model fit stats
'''


import os,sys
import argparse
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from numpy.random import seed
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from keras.layers import Input, Dense, LSTM, TimeDistributed, RepeatVector
from keras.models import Model
from keras import regularizers

seed(54321)
tf.random.set_seed(54321)

def load_training_data(training_data):
    try:
        rawdata = pd.read_csv(training_data, sep=',')#, names=header_names)
        print(rawdata.head())
        return rawdata
    except Exception as e:
        print('[ EXCEPTION ] {}'.format(e))
        sys.exit()

def split_train_test(df):
    train_df, test_df = train_test_split(df, test_size=0.25, random_state=54321, shuffle=True)
    train_df = train_df.set_index(['gameid','datetimestamp']).sort_index()
    test_df  = test_df.set_index(['gameid','datetimestamp']).sort_index()
    print(f'''Training dataset shape:   {train_df.shape}''')
    print(f'''Test dataset shape:       {test_df.shape}''')
    print(f'''Training dataset:''')
    print(train_df.head())
    return train_df, test_df

def df_preprocessing(df):
    scaler = MinMaxScaler()
    transformed_df = scaler.fit_transform(df)
    transformed_df = transformed_df.reshape(transformed_df.shape[0], 1, transformed_df.shape[1])
    print(f'''Transformed DF Shape: {transformed_df.shape}''')
    return transformed_df

def autoencoder_model(df):
    inputs = Input(shape=(df.shape[1], df.shape[2]))
    
    L1 = LSTM(16, activation='relu', return_sequences=True, kernel_regularizer=regularizers.l2(0.00))(inputs)
    L2 = LSTM(4,  activation='relu', return_sequences=False)(L1)
    L3 = RepeatVector(df.shape[1])(L2)
    L4 = LSTM(4,  activation='relu', return_sequences=True)(L3)
    L5 = LSTM(16, activation='relu', return_sequences=True)(L4)
    
    output = TimeDistributed(Dense(df.shape[2]))(L5)
    model_obj = Model(inputs=inputs, outputs=output)
    model_obj.compile(optimizer='adam', loss='mae')
    model_obj.summary()
    
    return model_obj

def execute_model_training(model_obj, epochs=10, batch_size=10, validation_split=0.05):
    history = model_obj.fit(X_train, X_train, epochs=epochs, batch_size=batch_size,validation_split=validation_split).history
    return model_obj

def assess_model(model, model_threshold=0.275):
    X_pred = model.predict(X_train)
    X_pred = X_pred.reshape(X_pred.shape[0], X_pred.shape[2])
    X_pred = pd.DataFrame(X_pred, columns=train_df.columns)
    X_pred.index = train_df.index
    scored = pd.DataFrame(index=train_df.index)
    Xtrain = X_train.reshape(X_train.shape[0], X_train.shape[2])
    scored['Loss_mae'] = np.mean(np.abs(X_pred-Xtrain), axis = 1)
    print('[ INFO ] Train DF Loss MAE: {}'.format(scored['Loss_mae']))
    
    X_pred = model.predict(X_test)
    X_pred = X_pred.reshape(X_pred.shape[0], X_pred.shape[2])
    X_pred = pd.DataFrame(X_pred, columns=test_df.columns)
    X_pred.index = test_df.index
    scored = pd.DataFrame(index=test_df.index)
    Xtest = X_test.reshape(X_test.shape[0], X_test.shape[2])
    scored['Loss_mae'] = np.mean(np.abs(X_pred-Xtest), axis = 1)
    print('[ INFO ] Test DF Loss MAE: {}'.format(scored['Loss_mae']))
    
    scored['Threshold'] = model_threshold
    scored['Anomaly'] = scored['Loss_mae'] > scored['Threshold']
    print(scored.head())
    
    return scored

if __name__ == "__main__":
    '''
    # ONLY used for TESTING - Example Arguments
    args =  {
                "training_data":    "./data/game_event_logs.csv",
                "epochs":           10,
                "batch_size":       10,
                "validation_split": 0.05,
                "model_threshold":  0.275,
                "model_filepath":   './models/'
            }
    '''
    
    # Arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--training_data",      required=True,                      type=str,   help="Training data including filename and filepath")
    ap.add_argument("--epochs",             required=True,  default=10,         type=int,   help="Model epochs")
    ap.add_argument("--batch_size",         required=True,  default=10,         type=int,   help="Model batch size")
    ap.add_argument("--validation_split",   required=True,  default=0.05,       type=float, help="Model validation percentage (ie. 0.05 is 5%")
    ap.add_argument("--model_threshold",    required=True,  default=0.275,      type=float, help="Model threshold for anomalies")
    ap.add_argument("--model_filepath",     required=True,  default='./models/',type=str,   help="Saved model output directory")
    args = vars(ap.parse_args())
    
    # Load Data
    rawdata = load_training_data(args['training_data'])
    
    # Split into Train and Test DFs
    train_df, test_df = split_train_test(rawdata)
    
    # Apply any preprocessing or transformations
    X_train      = df_preprocessing(train_df)
    X_test       = df_preprocessing(test_df)
    
    # Compile Model
    model_obj = autoencoder_model(X_train)
    
    # Execute Model Training
    model = execute_model_training(model_obj, epochs=args['epochs'], batch_size=args['batch_size'], validation_split=args['validation_split'])
    
    # Model Assessment
    scored = assess_model(model, model_threshold=args['model_threshold'])
    # Save model
    model.save(args['model_filepath'], save_format='tf')


#ZEND
