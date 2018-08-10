# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 17:36:47 2018

@author: victoria
"""
import metar
from metar import Metar
import datetime

def gendate(date, day, hour, mint=0):
    dref = date
    deltadays = 0

    if hour==24:
        hour = 0
        deltadays +=1
    if  date.day!=day:
        deltadays +=1
    if deltadays!=0:
        dref += datetime.timedelta(days=deltadays)             

    d = datetime.datetime(dref.year,dref.month, dref.day, hour,mint) 
    return d


def aproxbyhour(date):
    d = datetime.datetime(date.year, date.month, date.day, date.hour, 0) 
    if date.minute>=30: 
        d = d + datetime.timedelta(hours=1)
    return d

debug = False

class MetarModel(Metar.Metar):
  
  def __init__( self, inputcode, handlers):
      """Parse code based on handlers"""
      self.code = inputcode              # original METAR code
      self.type = ''                # Code type
      self.station_id = None        # 4-character ICAO station code
      
      self.handlemsg(inputcode,handlers) 
 
  
  def handlemsg(self, msg, handlers):      
      code = msg + " "    # (the regexps all expect trailing spaces...)
      try:
          ngroup = len(handlers)
          igroup = 0
          while igroup < ngroup and code:
              pattern, handler, repeatable = handlers[igroup]
              if debug: print(handler.__name__,":",code)
              m = pattern.match(code)
              while m:
                  if debug: Metar._report_match(handler,m.group())
                  handler(self,m.groupdict())
                  code = code[m.end():]
                  if not repeatable: break
                  
                  if debug: print(handler.__name__,":",code)
                  m = pattern.match(code)
              igroup += 1
      except Exception as err:
          raise Metar.ParserError(handler.__name__+" failed while processing '"+code+"'\n"+" ".join(err.args))
          raise err
      if code:
          raise Metar.ParserError("Unparsed groups in body '"+code+"' while processing '"+code+"'")
