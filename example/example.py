import os
from turtle import mode
from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import tensorflow as tf
import Load_Event as load_event
import AIC
import STALTA
from geopy.distance import geodesic
from werkzeug.utils import secure_filename
import pymysql
from dbutils.pooled_db import PooledDB
from flask_cors import CORS
import EQCNN

db = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    database="mecnn",
    port=3306,
    cursorclass=pymysql.cursors.DictCursor)


model_path = r'E:\IEM\MECNN\models'
model_dict = {}
for dlen in range(300, 1100, 100):
    model = tf.keras.models.load_model(os.path.join(model_path, f'{dlen}.h5'))
    model_dict[f'm{dlen//100}'] = model

recods_path = r'E:\IEM\MECNN\example\EQrecords'
flist = os.listdir(recods_path)

Data = pd.DataFrame()
for file in flist:
    data = pd.read_csv(os.path.join(recods_path, file), names=range(8), sep='\s+')
    data = load_event.readData(data)

    if len(data) != 0:
        acc_data = data.loc[:,'acc']
        
    else:
        continue

    # STALTA粗略捡拾p波
    Ppick = STALTA.ppick_stalat(acc_data,2,0.1,8,100)  
    if Ppick != -1:
        # AIC修正 
        Parrival = AIC.ppick_aic(acc_data,Ppick,2,0.1,100)
        # 切片：3-10s
        acc_pt = acc_data[Parrival:Parrival+1000]
        
        acc_pt = pd.DataFrame(np.array(acc_pt).reshape(1,-1))
        
        acc_pt['epidist'] = data.loc[0, 'epidist']
        acc_pt['depth'] = data.loc[0, 'epidist']
        acc_pt['vs30'] = data.loc[0, 'vs30']
        acc_pt['epc_lat'] = data.loc[0, 'epc_lat']
        acc_pt['epc_long'] = data.loc[0, 'epc_long']

        acc_pt['file_path'] = os.path.join(recods_path, file) 

        Data = pd.concat([Data, acc_pt], axis=0).reset_index(drop=True)
        
    else:
        continue  

Magpre = pd.DataFrame()
for dlen in range(300, 1100, 100):
    model = model_dict[f'm{dlen//100}']
    magpre = EQCNN.eqcnn(model, Data, dlen)
    magpre.round(2)

    magpre['lat'] = Data['epc_lat']
    magpre['long'] = Data['epc_long']
    magpre['depth'] = Data['depth']
    magpre['wave_len'] = dlen
    magpre['file_path'] = Data['file_path']

    print(magpre)

    with db.cursor() as cursor:
        Data_tuple = magpre.apply(lambda x: tuple(x), axis=1).values.tolist()
        sql = """insert into example(magpre, latitude, longitude, depth, wave_len, file_path) values(%s, %s, %s, %s, %s, %s)"""
        cursor.executemany(sql, Data_tuple)

        db.commit()




