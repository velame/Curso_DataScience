#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 23:38:00 2018

@author: victoriavelame
"""

import os
import pandas as pd
import io

#
#def getdata_metartaf(dire,year,airport=None):
#    dfs = []
#    for fname in os.listdir(dire):
#        f = os.path.join(dire,fname)
#        #f = read_csv( , 'r')
#        rawdata = f.read()
#        f.close()
#        out = out + handlerawdata(rawdata, trange)
#    return dfs

db_dir ='../3.DBGenerator/output' 
df = pd.read_csv('../3.DBGenerator/output/2017/SBGR_2017.csv',index_col=0,parse_dates=[0])
#df = pd.read_csv('../3.DBGenerator/output/2016/SBGR_2016.csv',index_col=0,parse_dates=[0])
df = df.dropna(axis=0, how='any')

df.plot(y=["metar_wind","taf_wind"],style='.')

df = df[df.taf_wind<99]
df.plot(y=["metar_wind","taf_wind"],style='.')

df[0:100].plot(y=["metar_wind","taf_wind"],style='.')


df[0:500].plot(y=["metar_wind","taf_wind"],style='.')

df[0:100:6].plot.bar(y=["metar_wind","taf_wind"],style='.')

#####

df[0:200].plot.bar(y=["metar_TS","taf_TS"],style='.')

df.plot.scatter(y='metar_wind',x='taf_wind',alpha=1/15)
df.plot.scatter(x='metar_wind',y='taf_wind',alpha=1/15)
df.plot.scatter(x='metar_wind',y='taf_wind',c='metar_TS', colormap='jet',alpha=1/15)