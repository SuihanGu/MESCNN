
import math
import numpy as np


def ppick_aic(adata,apick,preAIC=2,postAIC=0,fs=100):
    aic_data=np.array(adata).reshape(-1,1)
    dataLen=len(aic_data)

    nowPick=apick                      
    prePick=preAIC*fs                               
    posPick=postAIC*fs                             
    AICsize=nowPick+posPick
    
    #如果p波到时点接近数据末尾
    if AICsize>dataLen:
        AICsize=dataLen     
    df_AIC=np.zeros(int(AICsize)).reshape(-1,1)    
    if nowPick-prePick<=0:
        prePick=nowPick-2

    for n in range(nowPick-prePick,int(AICsize)-1):   
        if nowPick-prePick<=0: 
            return(0)
            break            
        M=aic_data[nowPick-prePick-1:n+1]   
        N=aic_data[n+1:int(AICsize)+1]
        if M.var()==0 or N.var()==0: 
            continue        
        df_AIC[n]=(n-nowPick+prePick+2)*math.log(M.var())+((int(AICsize))-n-1)*math.log(N.var())
    
    AICmin=nowPick-prePick  
    if AICmin<=0:
        AICmin=nowPick
    p=df_AIC[int(AICmin):int(AICsize)].argmin()   
    Ppoint=p+nowPick-prePick   

    return Ppoint



