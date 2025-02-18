
from operator import eq
import numpy as np
import pandas as pd
from geopy.distance import geodesic
from settings import VS30_PATH

def readData(data):
    try:
        # acc data, Baseline correction
        acc_data = data.iloc[17:,:].astype('float64')
        acc_data = pd.DataFrame(np.array(acc_data).reshape(-1,1))
        acc_data = acc_data-np.array(acc_data).reshape(-1,1)[:500].mean()

        # head info
        eq_head = data.iloc[:15,:]
        epc_lat = round(float(eq_head.iloc[1, 1]), 4)
        if epc_lat == 'NaN':
            epc_lat = 0

        epc_long = round(float(eq_head.iloc[2, 1]), 4)
        if epc_long == 'NaN':
            epc_long = 0

        epc_depth = round(float(eq_head.iloc[3, 2]), 4)
        if epc_depth == 'NaN':
            epc_depth = 0

        mag = float(eq_head.iloc[4, 1])
        if mag == 'NaN':
            mag = 0

        

        st_name = eq_head.iloc[5, 2]

        Vs30 = pd.read_csv(VS30_PATH)
        vs30 = Vs30[Vs30['station_code']==st_name].iloc[0,1]
        
        st_lat = round(float(eq_head.iloc[6, 2]), 4)
        st_long = round(float(eq_head.iloc[7, 2]), 4)

        if mag == 0:
            epidist = 100
        else:
            epidist = geodesic((epc_lat, epc_long), (st_lat, st_long)).km

        # scale factor
        scale_factor_ab = eq_head.iloc[13, 2].split('(gal)/')
        scale_factor = float(float(scale_factor_ab[0])/float(scale_factor_ab[1]))

        acc_data = acc_data*scale_factor

        acc_data = pd.DataFrame(np.array(acc_data).reshape(-1,1), columns=['acc'])
        acc_data['epc_lat'] = epc_lat
        acc_data['epc_long'] = epc_long
        acc_data['mag'] = mag
        acc_data['st_name'] = st_name
        acc_data['st_lat'] = st_lat
        acc_data['st_long'] = st_long

        acc_data['epidist'] = epidist
        acc_data['depth'] = epc_depth
        acc_data['vs30'] = vs30

        return acc_data
    except:
        return pd.DataFrame()

if __name__ == '__main__':

    data = ''
    info = eq(data)