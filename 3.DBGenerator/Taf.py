# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 16:43:54 2018

@author: victoria
"""
import re
from metar import Metar
import datetime
import pandas as pd
from MetarModel import gendate, aproxbyhour, MetarModel

TYPE_RE = re.compile(r"^(?P<type>TAF)\s*")

MODIFIER_RE = re.compile(r"^(?P<mod>AMD|COR)\s*") 

STATION_RE =  re.compile(r"^(?P<station>[A-Z][A-Z0-9]{3})\s*")

TIME_RE = re.compile(r"""^(?P<day>\d\d)
                          (?P<hour>\d\d)
                          (?P<min>\d\d)Z?\s*""",
                          re.VERBOSE)

VALID_RE = re.compile(r"^\s?(?P<iday>\d\d)(?P<ihour>\d\d)/(?P<eday>\d\d)(?P<ehour>\d\d)\s*")

WIND_RE = re.compile(r"""^(?P<dir>[\dO]{3}|[0O]|///|MMM|VRB)
                          (?P<speed>P?[\dO]{2,3}|[/M]{2,3})
                        (G(?P<gust>P?(\d{1,3}|[/M]{1,3})))?
                          (?P<units>KTS?|LT|K|T|KMH|MPS)?
                      (\s+(?P<varfrom>\d\d\d)V
                          (?P<varto>\d\d\d))?\s*""",
                          re.VERBOSE)
                      
VISIBILITY_RE = re.compile(r"""^(?P<vis>(?P<dist>(M|P)?\d\d\d\d|////)
                                        (?P<dir>[NSEW][EW]? | NDV)? |
                                        (?P<distu>(M|P)?(\d+|\d\d?/\d\d?|\d+\s+\d/\d))
                                        (?P<units>SM|KM|M|U) | 
                                        CAVOK )\s*""",re.VERBOSE)

WEATHER_RE = re.compile(r"""^(?P<int>(-|\+|VC)*)
                             (?P<desc>(MI|PR|BC|DR|BL|SH|TS|FZ)+)?
                             (?P<prec>(DZ|RA|SN|SG|IC|PL|GR|GS|UP|/)*)
                             (?P<obsc>BR|FG|FU|VA|DU|SA|HZ|PY)?
                             (?P<other>PO|SQ|FC|SS|DS|NSW|/+)?
                             (?P<int2>[-+])?\s+""",
                             re.VERBOSE)

SKY_RE= re.compile(r"""^(?P<cover>VV|CLR|SKC|SCK|NSC|NCD|BKN|SCT|FEW|[O0]VC|///)
                        (?P<height>[\dO]{2,4}|///)?
                        (?P<cloud>(CB|TCU|///))?\s*""",
                        re.VERBOSE)

TX_RE = re.compile(r"^TX(?P<tmax>\d\d)/(?P<day>\d\d)(?P<hour>\d\d)Z\s*")

TN_RE = re.compile(r"^TN(?P<tmin>\d\d)/(?P<day>\d\d)(?P<hour>\d\d)Z\s*")

GROUP_RE = re.compile ( "^(?P<group>FM|PROB\d{1,2}\s*(TEMPO)?|TEMPO|BECMG)\s*(?P<msg>[A-Z0-9\+\-/\s$]+?)(?=FM|PROB|TEMPO|BECMG|RMK|$)")

RMK_RE = re.compile (r"^RMK\s*(?P<trig>[A-Z]{3})?\s*$" )

class Taf(MetarModel):
    
    def __init__(self,date,tafcode):
      
      self.date   = date
      self.code   = tafcode              # complete and original TAF code
      self.type   = 'TAF'                # TAF 
      self.mod    = ''                   # AMD (emenda) or COR (corrected)
      self.station_id = None             # 4-character station code
      self.time = None                   # observation time [datetime]
      self.valid     = []
      self.wind_dir   = None             # wind direction [direction]
      self.wind_speed = None             # wind speed [speed]
      self.wind_gust  = None             # wind gust speed [speed]
      self.vis        = None             # visibility [distance]
      self.weather    = []               # present weather (list of tuples)
      self.sky        = []               # sky conditions (list of tuples)
      self.tmax = None
      self.tmin = None
      self.groups = [] #taf groups like TEMPO, BECMG, PROB 
      self.cavok = False
      self.rmktrig = None
      self.recent = []

      MetarModel.__init__(self,tafcode,self.tafhandlers)
      self.tafobjs   = self.tafbyhour()
      self.groupobjs = self.readgroups()
      self.update_tafbyhour()

    def update_tafbyhour(self):
        for gobj in self.groupobjs:
            start, end = gobj.valid
            if not 'TEMPO' in gobj.group: end =self.valid[1]
            for tobj in self.tafobjs:
                if tobj.time>=start and tobj.time<=end:
                    tobj = self.fillobj(gobj,tobj)


    def readgroups(self):
      tempobjs = []
      for g in self.groups:
          tempobj = MsgTaf(self.date)
          tempobj.group = g[0]
          if tempobj.group =='FM':
              tempobj.handlemsg(g[1],self.fmhandlers)
          else:
              tempobj.handlemsg(g[1],self.grouphandlers)
          tempobjs.append(tempobj)
      return tempobjs
    
    def tafbyhour(self):
        tafobjs = []
        timerange = pd.date_range(self.valid[0], self.valid[1], freq='H')
        for t in timerange:
            obj = MsgTaf(self.date)
            obj = self.filltafhour(obj,t)
            tafobjs.append(obj)
        return tafobjs
                
    def filltafhour(self,obj,time):
        obj.time        = time
        obj.station_id  = self.station_id
        obj.wind_dir    = self.wind_dir
        obj.wind_speed  = self.wind_speed        
        obj.wind_gust   = self.wind_gust
        obj.vis         = self.vis
        obj.weather     = self.weather
        obj.sky         = self.sky
        return obj

    def fillobj(self,g, t):
        t.group       = g.group
        t.cavok       = g.cavok
        if g.wind_dir:   t.wind_dir    = g.wind_dir
        if g.wind_speed: t.wind_speed  = g.wind_speed    
        if g.wind_gust:  t.wind_gust   = g.wind_gust
        if g.vis:        t.vis         = g.vis
        if g.group=='FM':
            t.weather     = g.weather
            t.sky         = g.sky
        else:
            if g.weather or g.cavok:    t.weather     = g.weather
            if g.sky or g.cavok:        t.sky         = g.sky
        return t
    
    def _handleTime(self,d):
        day, hour, mint = int(d['day']),int(d['hour']), int(d['min'])
        i = gendate(self.date, day, hour, mint)
        i = aproxbyhour(i)
        self.time = i
    
    def _handleFMTime(self,d):
        day, hour, mint = int(d['day']),int(d['hour']), int(d['min'])
        i = gendate(self.date, day, hour, mint)        
        i = aproxbyhour(i)
        self.valid = [i, None]
    
    def _handleValid(self,d):
        iday, ihour = int(d['iday']),int(d['ihour'])
        eday, ehour = int(d['eday']),int(d['ehour'])
        
        i = gendate(self.date, iday,ihour)
        e = gendate(self.date, eday,ehour)

        self.valid = [i,e]
    
    def _handleTx(self,d):
        self.tmax = int(d['tmax'])

    def _handleTn(self,d):
        self.tmin = int(d['tmin'])

    def _handleGroup(self,d):
        self.groups.append( (d['group'],d['msg']) )

    def _handleVisibilityCavok(self,d):
        self._handleVisibility(d)
        if  'CAVOK' in d['vis']:
            self.cavok = True 
            
    def _handleRMK(self,d):
        self.rmktrig = d['trig']
 
    tafhandlers = [ 
               (TYPE_RE, Metar.Metar._handleType, False),
               (MODIFIER_RE, Metar.Metar._handleModifier, False),
               (STATION_RE, Metar.Metar._handleStation, False), 
               (TIME_RE, _handleTime, False), 
               (VALID_RE, _handleValid, False),
               (WIND_RE, Metar.Metar._handleWind, False), 
               (VISIBILITY_RE,_handleVisibilityCavok, False), 
               (WEATHER_RE, Metar.Metar._handleWeather, True), 
               (SKY_RE, Metar.Metar._handleSky, True), 
               (TX_RE, _handleTx, False), 
               (TN_RE, _handleTn, False),
               (TX_RE, _handleTx, False),
               (GROUP_RE, _handleGroup, True),
               (RMK_RE, _handleRMK, False)]

    grouphandlers = [ 
               (VALID_RE, _handleValid, False),
               (WIND_RE, Metar.Metar._handleWind, False), 
               (VISIBILITY_RE, _handleVisibilityCavok, False), 
               (WEATHER_RE, Metar.Metar._handleWeather, True), 
               (SKY_RE, Metar.Metar._handleSky, True)]

    fmhandlers = [ 
               (TIME_RE, _handleFMTime, False),
               (WIND_RE, Metar.Metar._handleWind, False), 
               (VISIBILITY_RE,_handleVisibilityCavok, False), 
               (WEATHER_RE, Metar.Metar._handleWeather, True), 
               (SKY_RE, Metar.Metar._handleSky, True)
               ]

class MsgTaf(Taf):
    def __init__(self,date):
      self.date       = date

      self.station_id = None             # 4-character ICAO station code
      self.time       = None             # observation time [datetime]

      self.group     =  'TAF'
      self.valid     = []

      self.wind_dir   = None             # wind direction [direction]
      self.wind_speed = None             # wind speed [speed]
      self.wind_gust  = None             # wind gust speed [speed]
      self.vis        = None             # visibility [distance]
      self.weather    = []               # present weather (list of tuples)
      self.sky        = []               # sky conditions (list of tuples)
      self.recent = []
      self.cavok = False
    
      


class TestTaf:
    
    msg0 ='TAF SBGR 200840Z 2012/2118 07007KT CAVOKTX35/2018Z TN21/2108ZBECMG 2016/2018 06005KTFM202000 18005KT 8000 FEW040PROB30 TEMPO 2020/2023 TSRA SCT040 FEW050CBBECMG 2023/2101 11003KT CAVOKBECMG 2103/2105 08004KTBECMG 2111/2113 06006KTPROB30 2115/2117 35005KT RMK PGM'
    
    msgerr0 ='TAF SBGR 200840Z 2012/2118 07007KT 9999 TS FEW030XX TX35/2018Z TN21/2108Z RMK PGM'

    date = datetime.datetime(2015,1,1)

    def test0(self):
        t = Taf(self.date,self.msg0)
        self.printtaf(t)
        self.printobjs(t.tafobjs)

    def testerr0(self):
        try:
            Taf(self.date,self.msgerr0)
            print('Error: a wrong msg passed!')
        except:    
            print('Passed on test!')

    
    def printobjs(self, objs):
        for obj in objs:
            print(obj.time, obj.wind_speed.value(), obj.vis.value(), obj.sky, obj.weather)
    
    def printtaf(self,t):
        print(t.code)
        print(t.station_id, t.valid, t.wind_speed.value(), t.vis.value(), t.weather, t.sky)
        print(t.tmax, t.tmin)
        print(t.groups)
        
if __name__=='__main__':
    testtaf = TestTaf()
    testtaf.test0()
    testtaf.testerr0()
    
