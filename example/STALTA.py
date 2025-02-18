
import numpy as np


def ppick_stalat(sdata,ltw=2,stw=0.1,R=8,fs=100): 
    #画特征图
    Data=np.array(sdata).reshape(-1,1)
    CFp=(Data+0.01)**2
    numStw=stw*fs
    numLtw=ltw*fs
    len_data=len(Data)
    if numStw>len_data:
        numStw=len_data
    if numLtw>len_data:
        numLtw=len_data
    #实现三段捡拾
    STA_LTA=np.zeros(len_data).reshape(-1,1)
    STA_LTA[0]=1
    for i in range(1,int(numStw)):
        STA_LTA[i]=1
        
    for j in range(int(numStw),int(numLtw)):
        STA=(np.abs(CFp[j-int(numStw):j]).sum())/float(numStw)
        LTA=(np.abs(CFp[:j]).sum())/float(j)
        STA_LTA[j]=STA/LTA

    for k in range(int(numLtw),len_data):    
        STA=(np.abs(CFp[k-int(numStw):k]).sum())/float(numStw)
        LTA=(np.abs(CFp[k-int(numLtw):k]).sum())/float(numLtw)
        STA_LTA[k]=STA/LTA

    for m in range(len_data):   
        if STA_LTA[m]>R:
            c=m
            break 
        else:
            c=-1
    spick=c
    if spick==len_data:
        spick=-1
    return spick