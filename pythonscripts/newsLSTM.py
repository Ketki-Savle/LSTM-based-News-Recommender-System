
# coding: utf-8

# In[261]:

import json
import numpy as np
import matplotlib.pyplot as plt
#import pandas
import math
import sys
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.layers import LSTM, GRU
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import keras.backend as K
from keras.callbacks import ModelCheckpoint
from keras.callbacks import Callback
from keras.callbacks import TensorBoard
from keras.regularizers import L1L2

# In[253]:


class LossHistory(Callback):
    def on_train_begin(self, logs={}):
        self.losses = {'val_loss':[], 'val_cosine_proximity':[], 'loss':[], 'cosine_proximity':[]}

    def on_batch_end(self, batch, logs={}):
        self.losses['val_cosine_proximity'].append(logs.get('val_cosine_proximity'))
        self.losses['val_loss'].append(logs.get('val_loss'))
        self.losses['cosine_proximity'].append(logs.get('cosine_proximity'))
        self.losses['loss'].append(logs.get('loss'))

def batch_generator(x, t):
    i=0
    while True:
        if i == len(x):
            i=0
        else:
            xtrain, ytrain=x[i], t[i]
            i +=1
        yield xtrain, ytrain


# In[255]:


def LSTMbyTime(Xtrain, Ttrain,  Xtest, Ttest, epochs):
    K.clear_session()
    model = Sequential()
    model.add(LSTM(32, input_shape=(None, Xtrain[0].shape[2]), return_sequences=False, kernel_regularizer=L1L2(0, 0.1), dropout=0.5))
#    model.add(LSTM(1024, input_shape=( None, Xtrain[0].shape[2]), kernel_regularizer=L1L2(0.01, 0.01),dropout=0.5))
    model.add(Dense(1024))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(Ttrain[0].shape[1]))
    model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['cosine'])
    model.summary()
    val_steps=len(Xtest)
    steps_per_epoch=len(Xtrain)
    filepath="time_weights.best.model"
    losshist = LossHistory()
    checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
    TB=TensorBoard(log_dir='./Graph_time_best', histogram_freq=0, write_graph=True, write_images=True)
    callbacks_list = [checkpoint, TB, losshist]
    history=model.fit_generator(batch_generator(Xtrain, Ttrain), steps_per_epoch=steps_per_epoch,epochs=epochs, validation_data=batch_generator(Xtest, Ttest), callbacks=callbacks_list, verbose=2, validation_steps=val_steps)
    return {'model':model, 'history':history, 'losshist':losshist.losses}
    


# In[256]:


def LSTMbyFixSeq(Xtrain, Ttrain, Xtest, Ttest, batch_size, epochs):
    K.clear_session()
    filepath="fixed_weights.best.model"
    checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
    TB=TensorBoard(log_dir='./Graph_fixed_best', histogram_freq=0,  
          write_graph=True, write_images=True)
    losshist = LossHistory()
    callbacks_list = [checkpoint, TB, losshist]
    model = Sequential()
    model.add(LSTM(256, input_shape=(Xtrain.shape[1], Xtrain.shape[2]), kernel_regularizer=L1L2(0.00, 0.6693497970822383), dropout=0.384051579948428, return_sequences=True))
    model.add(LSTM(512, input_shape=(Xtrain.shape[1], Xtrain.shape[2]), kernel_regularizer=L1L2(0.00,  0.2232551758526089), dropout=0.5226618564648536))
    model.add(Dense(512))
    model.add(Activation('relu'))
#    model.add(Dropout(0.5))
    model.add(Dense(Ttrain.shape[1]))
    model.compile(loss='mean_squared_error' , optimizer='rmsprop', metrics=[ 'cosine'])
    model.summary()
    history=model.fit(Xtrain, Ttrain,batch_size=batch_size,epochs=epochs, callbacks=callbacks_list, verbose=2, validation_data=(Xtest, Ttest))
    return {'model':model, 'history':history, 'losshist':losshist.losses}


# In[258]:


def main(args):
    x_file=args[0]
    t_file=args[1]
    x_cold=args[2]
    t_cold=args[3]
    model=args[4]
    Xtrain=np.load(x_file)
    Ttrain=np.load(t_file)
    Xtest=np.load(x_cold)
    Ttest=np.load(t_cold)
    if model == 'time':
        test=LSTMbyTime(Xtrain, Ttrain, Xtest, Ttest, epochs=10)
    elif model == 'fixed':
        test=LSTMbyFixSeq(Xtrain, Ttrain, Xtest, Ttest, batch_size=50, epochs=10)
    with open(model+'history.json','w') as f:
        json.dump(test['history'].history, f)
    np.save(model+'perbatchhistory.npy', test['losshist'])


# In[262]:


if __name__ == '__main__':
    main(sys.argv[1:])

