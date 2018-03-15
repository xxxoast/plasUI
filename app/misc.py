#coding:utf-8 
import time
from pandas import to_datetime

unicode2utf8 = lambda x: x.encode('utf-8') if isinstance(x,unicode) else x
unicode2cp936 = lambda x: x.encode('cp936') if isinstance(x,unicode) else x

def timeint2str(inttime):
    inttime = inttime if isinstance(inttime,int) else int(inttime)
    hour,min,sec = inttime/10000,(inttime%10000)/100,inttime%100
    return ':'.join((str(hour),str(min),str(sec)))

def diff_seconds(now, last):
    #format [date,second]
    if last[0] == -1 or last[1] == -1:
        return 24 * 3600
    now_day, last_day = to_datetime(str(now[0])), to_datetime(str(last[0]))
    diff_date_seconds = (now_day - last_day).days * 24 * 60 * 60
    diff_tstamp_seconds = (int(now[1]/10000) - int(last[1]/10000)) * 3600 + \
                            ( int( (now[1]%10000)/100 ) - int( (last[1]%10000)/100 ) ) * 60 + \
                              ((now[1]%100) - (last[1]%100))
    gap_seconds = diff_date_seconds + diff_tstamp_seconds
    return gap_seconds
    
def unicode2str_r(obj):
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.iteritems():
            new_dict[unicode2str_r(k)] = unicode2str_r(v)
        return new_dict
    elif isinstance(obj, list):
        new_list = [unicode2str_r(i) for i in obj]
        return new_list
    elif isinstance(obj, unicode):
        return str(obj)
    else:
        return obj

def unicode2utf8_r(obj):
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.iteritems():
            new_dict[unicode2utf8_r(k)] = unicode2utf8_r(v)
        return new_dict
    elif isinstance(obj, list):
        new_list = [unicode2utf8_r(i) for i in obj]
        return new_list
    elif isinstance(obj, unicode):
        return unicode2utf8(obj)
    else:
        return obj
   
def unicode2cp936_r(obj):
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.iteritems():
            new_dict[unicode2cp936_r(k)] = unicode2cp936_r(v)
        return new_dict
    elif isinstance(obj, list):
        new_list = [unicode2cp936_r(i) for i in obj]
        return new_list
    elif isinstance(obj, unicode):
        return unicode2cp936(obj)
    else:
        return obj 
    
def get_today():
    t = time.localtime()
    return t.tm_year * 10000 + t.tm_mon * 100 + t.tm_mday


def get_hourminsec():
    t = time.localtime()
    return t.tm_hour * 10000 + t.tm_min * 100 + t.tm_sec
