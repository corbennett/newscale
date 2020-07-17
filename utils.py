# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 15:53:24 2020

@author: svc_ccg
"""
import pandas as pd
import numpy as np
import logging

#This is the function that tries to find the insertion start and end times from the logged motor movements
def findInsertionStartStop(df, ztolerance=50):
    ''' Input: Dataframe from newscale log file for a specific date and probe serial number indexed by time stamps
            df is used to generate timeDeltas: Series datetime index of pandas dataframe (time between rows) in seconds
        Output: start and stop points where probe insertion is inferred to have started and stopped
        (based on pattern of many log entries at small time deltas with small z movements but no xy movement)'''
    
    timeDeltas = df.index.to_series().diff().astype('timedelta64[s]')
    rolling_time_delta = timeDeltas.rolling(20, win_type='boxcar').mean().shift(-19).dropna()
    
    deltas = df[['z','x','y']].diff().abs() #get deltas for each axis
    rolling = deltas.rolling(20, win_type='boxcar').mean().shift(-19).dropna() #average over 20 steps and shift to left align
    #find the first time such that there are small steps in Z and no movement in X and Y AND the time steps are small
    try:    
        insertion = rolling.where((rolling['z']<10)&
                                              (rolling['z']>0)&
                                              (rolling['x']<1)&
                                              (rolling['y']<1)&
                                              (rolling_time_delta<2)).dropna()
     
        start = insertion.index[0]    
        insertion_deltas = deltas[start:].dropna()
        first_big_z = insertion_deltas.where(insertion_deltas['z']>ztolerance).dropna()
        # first_big_time = timeDeltas[start:].where(timeDeltas[start:]>300).dropna()
        # if len(first_big_time)>0:
        #     end = first_big_time.index[0]
        if len(first_big_z)>0:
            end = deltas[start:first_big_z.index[0]].index[-2]
        else:
            end = timeDeltas[start:][timeDeltas[start:]<10].index[-2] #find last point at short time delta

        print(end-start)
        
    except Exception as e:
        logging.exception(e)
        start, end = deltas.index[0], deltas.index[0]
    return start, end