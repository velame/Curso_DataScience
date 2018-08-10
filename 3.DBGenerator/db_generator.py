#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 15:07:47 2018

@author: victoriavelame
"""

import os
import pandas as pd
import datetime
from metar import Metar
from Taf import Taf
import time

def gendatetime(datestr):
        year  = int(datestr[0:4])
        month = int(datestr[4:6])
        day   = int(datestr[6:8])
        hour  = int(datestr[8:10])

        return datetime.datetime(year,month,day,hour)

def time2strsYmdH(date):
    return date.strftime(format="%Y%m%d%H")

###### Funtions to handle with archives #######################################
def handlerawdata(raw, trange):
    out = []
    for e in raw.split('\n'):
        if e and e[-1]=='=':
            date = e[0:10]
            msg  = e[13:-1]
            if date >= trange[0] and date <= trange[1]: out.append( {'date':date,'msg':msg})
    return out

def getalldata(dire, trange):
    out = []
    for filename in os.listdir(dire):
        fdire   = os.path.join(dire,filename)
        f = open( fdire, 'r')
        rawdata = f.read()
        f.close()
        out = out + handlerawdata(rawdata, trange)

    return out

###### Funtions to handle with archives #######################################

#DATABASE structure by airport (type pandas Panel)
# metar data, taf data, wo data (DataFrame by airp: wind, weather, cloud)
#DB columns, indexed by date

class DataBase:

    def __init__(self,init,end):
        self.timerange = [init, end]
        self.columns = self.getcolumns()
        self.dates = pd.date_range(init, end, freq='H')
        self.pdb = pd.Panel(minor_axis=self.columns, major_axis=self.dates)
        self.handledict = self.genhandledict()

    def getcolumns(self):
        col   = []
        for h in self.colstruct:
            msgtype = h[0]
            for phem in h[1]:
                col.append(msgtype + '_' + phem)
        return col

    def genhandledict(self):
        h = {}
        i = 0
        for mod in self.colstruct:
            v = []
            n = i
            for p in mod[1]:
                i +=1
                v.append(self.handlers[p])
            h[mod[0]] = [n,i,v]
        return h


    def emptydf(self):
        df = pd.DataFrame(columns=self.columns,index=self.dates)
        return df

    def update(self, msg,obj):
        if not (obj.station_id in self.pdb.items):
            self.pdb[obj.station_id] = self.emptydf()
        self.updatedf(obj.station_id,msg,obj)

    def updatedf(self,airp,msg,obj):
        if obj.time <= self.timerange[1]:
            index = self.index(obj.time)

            v = []
            n0,n1, handlelist = self.handledict[msg]
            for handle in handlelist:
              v.append( handle(self,obj) )
            self.pdb[airp].values[index][n0:n1] = v

    def updatedftaf(self,objs):
        airp = objs[0].station_id
        if not (airp in self.pdb.items):
            self.pdb[airp] = self.emptydf()

        first_index = self.index(objs[0].time)
        last_index  = self.index(objs[-1].time)
        n0,n1, handlelist = self.handledict['taf']

        vectdf = []
        for obj in objs:
            if obj.time <= self.timerange[1]:
                v = []
                for handle in handlelist:
                  v.append( handle(self,obj) )
                vectdf.append(v)

        self.pdb[airp].values[first_index:last_index+1, n0:n1] = vectdf




    def index(self,date_time):
        delta = date_time -  self.timerange[0]
        index = round(delta.days*24 + delta.seconds/3600.0)
        return index

    def getTS(self,obj):
        return self.getweather(obj,'TS')

    def getGRGS(self,obj):
        return self.getweather(obj,'GR') or self.getweather(obj,'GS')

    def getSQ(self,obj):
        return self.getweather(obj,'SQ')

    def getCB(self,obj):
        return self.getcloud(obj,'CB')

    def getTCU(self,obj):
        return self.getcloud(obj,'TCU')

    def getOBS(self,obj):
        obs = 1
        if obj.obs=='FCST': obs=0
        return obs

    def getspeedwind(self,obj):
        w = None
        if obj.wind_speed:
            w = obj.wind_speed.value()
            if obj.wind_gust:
               w = max(obj.wind_gust.value(),obj.wind_speed.value())
        return w

    def getweather(self, obj, phem='all'):
        """   1 have phem, 0 don't have phem
              weather and recent [list of tuples]
              (intensity, description, precipitation, obscuration, other)
        """
        w = 0
        vww = obj.weather + obj.recent
        for ww in vww:
            if (phem in ww):
                w = 1
        if phem =='all': w = vww

        return w

    def getcloud(self, obj, phem='all'):
        """
          1 have phem, 0 don't have phem
          sky [list of tuples]
          (cover, height, cloud)
        """
        c = 0
        vc = [ (t[0],t[1].value(),t[2]) if t[1] else (t[0],t[1],t[2]) for t in obj.sky]
        for e in vc:
            if (phem in e):
                c = 1
        if phem =='all': c = vc

        return c

    def genexcel(self,name,airplist=None):
        '''If airplist is empty all airports are catched. Airplist needs to be a list of airports'''
        writer = pd.ExcelWriter(name+'.xlsx', engine='xlsxwriter')
        if airplist:
            self.pdb[airplist].to_excel(writer)
        else:
            self.pdb.to_excel(writer)
        writer.save()

    def gencsv(self,year):
        '''If airplist is empty all airports are catched. Airplist needs to be a list of airports'''
        for air in self.pdb.items:
            df = self.pdb[air]
            df.to_csv('./output/'+year+'/'+air+'_'+year+'.csv')
            


    intrphem  = ['wind', 'TS', 'GRGS', 'CB', 'TCU']
    colstruct = [ ('metar',intrphem), ('taf',intrphem) ]

    handlers  = { 'wind':getspeedwind,
                  'TS'  :getTS,
                  'GRGS':getGRGS,
                  'CB'  :getCB,
                  'TCU' :getTCU}


##############################################################################


def readmetar(per,db):
    #Get metar brute data
    dire   = os.path.join('./input/raw_data','metar')
    vmetar = getalldata(dire, per)

    metarerror = []
    for el in vmetar:
        try:
            ely,elm = int(el['date'][0:4]), int(el['date'][4:6])
            m = Metar.Metar(el['msg'],year=ely,month=elm)
            db.update('metar',m)
        except:
            metarerror.append(el)
    return db

def readtaf(per,db):
    #Get taf brute data
    dire   = os.path.join('./input/raw_data','taf')
    vtaf   = getalldata(dire, per)

    taferror = []
    for el in vtaf:
        try:
            t = Taf( gendatetime(el['date']) ,el['msg'])
            db.updatedftaf(t.tafobjs)
#            for obj in t.tafobjs:
#                db.update('taf',obj)
        except:
            taferror.append(el)
    return db


def main():

    ########### INPUTS: ###########################################################
    year = "2017"
    
    ######################################################################
    period    = [year + '010100', year+'123123'] #[start date, end date ] #yymmddhh
    
    localtime = time.asctime( time.localtime(time.time()) )
    database = DataBase( gendatetime(period[0]), gendatetime(period[1]) )
#
    print("reading metar ")
    database = readmetar(period,database)

    print("reading taf ")
    database = readtaf(period,database)

    #write excel file
    print("writing excel ")
    database.gencsv(year)

    return database




import cProfile, pstats, io
pr = cProfile.Profile()
pr.enable()
db = main()
pr.disable()
s = io.StringIO()
sortby = 'tottime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue()[0:2000])

#TODO fast pdb to csv or xls faster one way to export to a panel to excel

