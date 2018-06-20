# -*- coding: utf-8 -*-
import re
import math
import random
import requests
import datetime
from threading import Timer
from time import sleep
from bs4 import BeautifulSoup as bs
from Crypto.Cipher import XOR
import base64
import constants, common

# consatns included
CONSTANTS = constants.export()
smart_office_base_url = CONSTANTS['smart_office_base_url']

# encrypt key
encrypt_key = 'Smart Office'

# OT schedule time
OT_schedule_time = '10:14'

login_url = smart_office_base_url + '/logon.aspx?ReturnUrl=%2ffoxconn%2fDefault.aspx'
get_access_token_url = smart_office_base_url + '/services/get_services.ashx'
get_attenance_url = smart_office_base_url + '/AppOnTimev3/services/GetByUserRange.ashx'

# login smart office
def login(s, UserName, Password):
    login_get = s.get(login_url)
    soup_login_get = bs(login_get.text, 'lxml')
    login_post_body = {
        '__LASTFOCUS': soup_login_get.select('#__LASTFOCUS')[0]['value'],
        '__VIEWSTATE': soup_login_get.select('#__VIEWSTATE')[0]['value'],
        '__EVENTTARGET': 'butLogin',
        '__EVENTARGUMENT': 'OnClick',
        '__EVENTVALIDATION': soup_login_get.select('#__EVENTVALIDATION')[0]['value'],
        'UserName': UserName,
        'Password': Password,
        'Language': 'tw',
    }
    res_login = s.post(login_url, data = login_post_body)
    if len(bs(res_login.text, 'lxml').select('#UserName')):
        return False
    else:
        return True

# retrive the access token of this session
def get_access_token(s):
    res_get_access_token = s.get(get_access_token_url, params = {'timestamp': common.now_timestamp()})
    access_token = common.dic_text_to_dic(res_get_access_token.text)['data']['access_token']
    return access_token

# extract "user" data
def extract_user_data(abd):
    e_data = {
      "USER_ID": abd['USER_ID'],
      "USER_NAME": abd['USER_NAME'].decode('utf8'),
      "USER_SITE": abd['USER_SITE'].decode('utf8'),
      "CURRENT_OU_CODE": abd['CURRENT_OU_CODE'],
      "CURRENT_OU_NAME": abd['CURRENT_OU_NAME'].decode('utf8')
    }
    return e_data

# get user info.
def get_user_info(s, access_token, query_date_start, query_date_end):
    query_data = {
        'StartDate': query_date_start.strftime('%Y/%m/%d'),
        'EndDate': query_date_end.strftime('%Y/%m/%d')
    }
    get_attenance_res = s.get(get_attenance_url, params = query_data)
    extracted_data = extract_user_data(common.dic_text_to_dic(get_attenance_res.text))
    return extracted_data

# count the "delay" required from time_1 to time_2
def count_next_time_in_seconds(time_1, time_2 = OT_schedule_time):
    t2_datetime = datetime.datetime.strptime(time_2, '%H:%M')
    t1_datetime = datetime.datetime.strptime(time_1, '%H:%M')
    next_delay_seconds = int((t2_datetime - t1_datetime).total_seconds())
    if (t2_datetime - t1_datetime).total_seconds() < 10:
        # choose the next day to execute
        next_delay_seconds = next_delay_seconds + 24*60*60
    return next_delay_seconds
    
# clear unused thread Timer to avoid memory leak
def clear_timer(timer):
    timer.cancel()
    del timer

# threading.Timer only supports "once"
# determine_success_fn returns 
def do_job_once(wrapped_job, job_arg, determine_success_fn, rec_timers):
    result = wrapped_job(job_arg)
    if determine_success_fn(result): # no need to schedule
        pass
    else:
        schedule_job(wrapped_job, job_arg, determine_success_fn, rec_timers)
        
    
# common schedule
# hard code every day <OT_schedule_time>
# return job_obj
def schedule_job(job, job_arg, determine_success_fn, rec_timers = []):
    now_time = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M')
    delay_seconds = count_next_time_in_seconds(now_time)
    new_schedule = Timer(delay_seconds, do_job_once, (job, job_arg, determine_success_fn, rec_timers))
    rec_timers.append(new_schedule)
    new_schedule.start()
    return rec_timers

# cancel common schedule
def cancel_job(rec_timers):
    for timer in rec_timers:
        clear_timer(timer)
    del rec_timers
    print 'Clear all timers'

# simple encrypt funtion that can be decrypt
def encrypt(plaintext, key = encrypt_key):
    cipher = XOR.new(key)
    return base64.b64encode(cipher.encrypt(plaintext))

# simple decrypt function
def decrypt(ciphertext, key = encrypt_key):
    cipher = XOR.new(key)
    return cipher.decrypt(base64.b64decode(ciphertext))