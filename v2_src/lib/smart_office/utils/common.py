# -*- coding: utf-8 -*-
import re
import datetime
import constants

CONSTANTS = constants.export()

# JS stringified json to python dic
def dic_text_to_dic(text):
    replaced = text.replace('false', 'False').replace('true', 'True').replace('null', 'None')
    return eval(replaced)

# timestamp now (in seconds)
def now_timestamp():
    secs = (datetime.datetime.now() - datetime.datetime(1970, 1, 1, 8)).total_seconds()
    return int(secs)

# python utf string to response JSON text
def utf_to_res_text(text):
    return str(text).replace('"', '').replace('u\'', '\'').replace('\'','"')

# special date format in smart office
def specail_date_format_to_date(st):
    timestamp = float(re.search('\\\\\/Date\((\d+)\)\\\\\/', st).group(1))/1000
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

# special time format in smart office
def specail_date_format_to_time(st):
    timestamp = float(re.search('\\\\\/Date\((\d+)\)\\\\\/', st).group(1))/1000
    return datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M')

# time_str is in the format %H:%M
def formal_time_str_to_special_format(time_str):
    time_struc = datetime.datetime.strptime(time_str, '%H:%M')
    time_hour = time_struc.hour
    time_min = time_struc.minute
    if time_hour >= 12:
        keyword = CONSTANTS['evening_keyword']
    else:
        keyword = CONSTANTS['morning_keyword']
    time_format = datetime.datetime(1900, 1, 1, time_hour, time_min).strftime('%I:%M') + ' ' + keyword
    return time_format
