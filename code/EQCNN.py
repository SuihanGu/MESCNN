import os
import numpy as np
import pandas as pd
import tensorflow as tf


# model_path = r'D:\vscode project\LJA Project\python\MECNN\models'
def eqcnn(model, data, dlen):
    X_main = np.array(data.iloc[:,:dlen].astype('float32')).reshape(-1, 1, dlen, 1)
    X_aux = np.array(data[['epidist', 'depth', "vs30"]].astype('float32')).reshape(-1, 1, 3, 1)
    magpre = model.predict([X_main, X_aux])
    magpre = pd.DataFrame(np.array(magpre).reshape(-1,1), columns=['magpre']).round(2)

    return magpre
