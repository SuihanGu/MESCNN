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
from settings import MODEL_PATH, UPLOAD_FOLDER,HOST,USER,PASSWORD,DB

app = Flask(__name__)
CORS(app)

model_dict = {}
for dlen in range(300, 1100, 100):
    model = tf.keras.models.load_model(os.path.join(MODEL_PATH, f'{dlen}.h5'))
    model_dict[f'm{dlen//100}'] = model


sqlpool = PooledDB(
    pymysql,
    mincached=5,
    host=HOST,
    user=USER,
    passwd=PASSWORD,
    db=DB,
    port=3306,
    setsession=['SET AUTOCOMMIT = 1'],
    use_unicode=True)


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# 上传接口
@app.route('/mecnn/upload', methods=['GET', 'POST'])
def upload_file():
    try:
        if 'files' not in request.files:
            return jsonify({"error": "没有文件上传"}), 400

        files = request.files.getlist('files')
        if not files:
            return jsonify({"error": "没有选择文件"}), 400

        # 创建目录（如果不存在）
        folder = request.form.get('folder', 'default')  # 获取文件夹名称参数
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(folder_path, exist_ok=True)

        file_paths = []

        
        
        connsql = sqlpool.connection()
        with connsql.cursor() as cursor:
            cursor.execute("truncate table upload_files;")
        connsql.commit()
        
        # 保存每个文件
        for file in files:
            # if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(folder_path, filename)
            file.save(file_path)
            file_paths.append(file_path)

            # 将文件路径存入数据库
            connsql = sqlpool.connection()
            with connsql.cursor() as cursor:
        
                sql = "INSERT INTO upload_files (folder_name, file_name, file_path) VALUES (%s, %s, %s)"
                cursor.execute(sql, (folder, filename, file_path))
            
            connsql.commit()

            
        print(f"File paths: {file_paths}")
        return jsonify({"message": "File uploaded successfully", "file_path": file_paths}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# 展示上传的文件列表
@app.route('/mecnn/show', methods=['GET', 'POST'])
def get_files():
    try:
        connsql = sqlpool.connection()
        with connsql.cursor() as cursor:
            sql = sql = "SELECT * FROM upload_files"
            cursor.execute(sql)
            files = cursor.fetchall()
            
        connsql.commit()
        
        return jsonify({"files": files}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 根据前端返回的文件路径，进行数据处理、震级估算
@app.route("/mecnn/eqcnn", methods=["POST"])
def process_file():
    try:
        # 获取请求中的文件路径
        data_req = request.json
        file_path = data_req.get("file_path")
        dlen = data_req.get("dlen")
        dlen = int(dlen)
        
        
        # path_list = file_path['file_path']
        Data = pd.DataFrame()
        for i in range(len(file_path)):
            path_ = file_path[i]
            if not path_ or not os.path.exists(path_):
                return jsonify({"error": "文件路径不存在"}), 404
        
        # 处理数据
        # for path_ in range(file_path):
            data = pd.read_csv(path_, names=range(8), sep='\s+')
            data = load_event.readData(data)

            if len(data) != 0:
                acc_data = data.loc[:,'acc']
            else:
                return jsonify({"message": "数据异常!"})
            
            acc_data = data.loc[:,'acc']

            # STALTA粗略捡拾p波
            Ppick = STALTA.ppick_stalat(acc_data,2,0.1,8,100)  
            if Ppick != -1:
                # AIC修正
                Parrival = AIC.ppick_aic(acc_data,Ppick,2,0.1,100)

                acc_pt = acc_data[Parrival:Parrival+1000]
                acc_pt = pd.DataFrame(np.array(acc_pt).reshape(1,-1))

                acc_pt['epidist'] = data.loc[0, 'epidist']
                acc_pt['depth'] = data.loc[0, 'epidist']
                acc_pt['vs30'] = data.loc[0, 'vs30']
                acc_pt['epc_lat'] = data.loc[0, 'epc_lat']
                acc_pt['epc_long'] = data.loc[0, 'epc_long']

                acc_pt['file_path'] = path_
                Data = pd.concat([Data, acc_pt], axis=0).reset_index(drop=True)
            else:
                continue  

        model = model_dict[f'm{dlen//100}']
        magpre = EQCNN.eqcnn(model, Data, dlen)
        magpre['lat'] = Data['epc_lat']
        magpre['long'] = Data['epc_long']
        magpre['depth'] = Data['depth']
        magpre['wave_len'] = f"{dlen//100}s"
        magpre['file_path'] = Data['file_path']
        
        connsql = sqlpool.connection()
        with connsql.cursor() as cursor:
            Data_tuple = magpre.apply(lambda x: tuple(x), axis=1).values.tolist()
            print(Data_tuple[0])
            sql = """insert into magpre(magpre, latitude, longitude, depth, wave_len, file_path) values(%s, %s, %s, %s, %s, %s)"""
            cursor.executemany(sql, Data_tuple)
        connsql.commit()
                
        return magpre.to_dict()
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/mecnn/hist_magpre", methods=["GET", "POST"])
def get_his_magpre():
    try:
        connsql = sqlpool.connection()
        with connsql.cursor() as cursor:
            sql = sql = "SELECT * FROM magpre"
            cursor.execute(sql)
            data = cursor.fetchall()
        connsql.commit()
        
        return jsonify({"data": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
    




    


