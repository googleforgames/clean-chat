
# coding=utf-8
# Copyright 2020 Google LLC

'''
TODO:
    - Refactor for tfx pipeline
    - Add parameterization / args
    - Add feature engineering to enhance model
    - Add new model fit stats

'''

import os,re
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import seaborn as sns
sns.set(color_codes=True)
import matplotlib.pyplot as plt

from numpy.random import seed
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from keras.layers import Input, Dropout, Dense, LSTM, TimeDistributed, RepeatVector
from keras.models import Model
from keras import regularizers

seed(54321)
tf.random.set_seed(54321)

def load_data(data_dir='data/'):
    rawdata = pd.DataFrame()
    
    #header_names = ['datetimestamp','gameid','x_cord','y_cord','points','direction','speed']
    
    for filename in os.listdir(data_dir):
        if re.search('game_event_logs[0-9]*\.csv',filename.lower()):
            dataset = pd.read_csv(os.path.join(data_dir, filename), sep=',')#, names=header_names)
            rawdata = rawdata.append(dataset)
    
    print(rawdata.head())
    return rawdata

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

def assess_model(model, anomaly_threshold=0.275):
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
    
    scored['Threshold'] = anomaly_threshold
    scored['Anomaly'] = scored['Loss_mae'] > scored['Threshold']
    print(scored.head())
    
    return scored

if __name__ == "__main__":
    
    # Load Data
    rawdata = load_data(data_dir='data/')
    
    # Split into Train and Test DFs
    train_df, test_df = split_train_test(rawdata)
    
    # Apply any preprocessing or transformations
    X_train      = df_preprocessing(train_df)
    X_test       = df_preprocessing(test_df)
    
    # Compile Model
    model_obj = autoencoder_model(X_train)
    
    # Execute Model Training
    model = execute_model_training(model_obj, epochs=1, batch_size=10, validation_split=0.05)
    
    # Model Assessment
    scored = assess_model(model, anomaly_threshold=0.275)
    # Save model
    model.save('./models/', save_format='tf')


#ZEND
