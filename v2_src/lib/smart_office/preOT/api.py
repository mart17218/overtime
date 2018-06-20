# -*- coding: utf-8 -*-
# smart office preOT api
import re
import math
import random
import requests
import datetime
from time import sleep
from bs4 import BeautifulSoup as bs
from ..utils import constants, common, general

# consatns included
CONSTANTS = constants.export()
smart_office_base_url = CONSTANTS['smart_office_base_url']

# api related to preOT
if CONSTANTS['is_test']:
    preOT_url = smart_office_base_url + '/overtime_test/PreOT.aspx'
    get_preOT_list_url = smart_office_base_url + '/overtime_test/service/QueryOTCUser.ashx'
else:
    preOT_url = smart_office_base_url + '/overtime/PreOT.aspx'
    get_preOT_list_url = smart_office_base_url + '/overtime/service/QueryOTCUser.ashx'

# get the preOT list
def get_preOT_list(s, access_token, query_date_start, query_date_end):
    query_data = {
        'sotdate':query_date_start.strftime('%Y-%m-%d'),
        'eotdate':query_date_end.strftime('%Y-%m-%d'),
        'userinfo':'',
        'sstatus':'',
        'smethods':'',
        'curpagenum':'0',
        'processdate':'',
        'actpre':'預報'
    }
    # MUSTTT request 2 times...
    res = s.post(get_preOT_list_url, data = query_data, params = {'access_token': access_token})
    res = s.post(get_preOT_list_url, data = query_data, params = {'access_token': access_token})
    if res.text == '':
        return []
    preOT_data = common.dic_text_to_dic(res.text)
    try:
        preOT_data = map(lambda data: \
        {
            'date': common.specail_date_format_to_date(data['STARTTIME']),
            'desc': data['OTDESC'].decode('utf8'),
            'method': data['METHODS'].decode('utf8'),
            'arrive': common.specail_date_format_to_time(data['STARTTIME']),
            'leave': common.specail_date_format_to_time(data['ENDTIME']),
            'pre_ot_id': data['DOCNUM'],
            'hrs6': data['HRS6'],
            'status': data['DOCSTATUS'].decode('utf8')
        }, preOT_data)
        return preOT_data
    except:
        return []
    
# check it has preOT this day
def check_already_exists(s, access_token, day):
    result = get_preOT_list(s, access_token, day, day)
    if not len(result):
        return False
    else:
        return True
    
# day_type = workday / holiday
# POST a preOT at a day
def preOT_by_day(s, access_token, date, reason, method, day_type = 'workday'):
    now = datetime.datetime.now()
    if date.date() == now.date() and date.time() > datetime.time(18,30):
        return False
    if check_already_exists(s, access_token, date):
        return False
    res_service_proOT = s.get(preOT_url, params = {'access_token': access_token})
    soup = bs(res_service_proOT.text, 'lxml')
    if day_type is 'workday':
        fstime = common.formal_time_str_to_special_format(CONSTANTS['default_workday_overtime_start'])
        fetime = common.formal_time_str_to_special_format(CONSTANTS['default_workday_overtime_end'])
    else: # holiday
        fstime = common.formal_time_str_to_special_format(CONSTANTS['default_holiday_overtime_start'])
        fetime = common.formal_time_str_to_special_format(CONSTANTS['default_holiday_overtime_end'])
    post_OT_body = {
        '__WORKFLOWTARGET': 'apsoft.workflow.client.workflow',
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': 'Approve',
        '__VIEWSTATE': soup.select('#__VIEWSTATE')[0]['value'],
        '__EVENTVALIDATION': soup.select('#__EVENTVALIDATION')[0]['value'],
        '__WORKFLOWSTATE': soup.select('#__WORKFLOWSTATE')[0]['value'],
        '__COMMENT': '',
        '__WORKFLOWSEARCH': '',
        'fsdate': date.strftime('%Y-%m-%d'),
        'fstime': fstime,
        'fedate': date.strftime('%Y-%m-%d'),
        'fetime': fetime,
        'frestmin': '0',
        'fdesc': reason,
        'fmethods': method,
        'skey': ''
    }
    res_post_OT = s.post(preOT_url, data = post_OT_body, params = {'access_token': access_token})
    new_workflow_state = common.dic_text_to_dic(res_post_OT.text)['data']['workflowstate']
    post_OT_body['__WORKFLOWSTATE'] = new_workflow_state
    res_second_post_OT = s.post(preOT_url, data = post_OT_body)
    return res_second_post_OT.text

# function to handle "ot_len"
def ot_len_to_day(ot_len):
    now_date = datetime.datetime.now()
    if ot_len is 'd':
        return [now_date]
    elif ot_len is 'sat':
        to_next_saturday = 6 - int(now_date.strftime('%w'))
        if to_next_saturday % 7 > 0: # Not allow "today"
            saturday = now_date + datetime.timedelta(days = to_next_saturday)
            return [saturday]
        else:
            return False
    elif ot_len is 'sun':
        to_next_sunday = 7 - int(now_date.strftime('%w'))
        if to_next_sunday % 7 > 0: # Not allow "today"
            sunday = now_date + datetime.timedelta(days = to_next_sunday)
            return [sunday]
        else:
            return False
    elif ot_len is 'w':
        all_days = []
        for day in range(6 - int(now_date.strftime('%w'))):
            all_days.append(now_date + datetime.timedelta(days = day))
        return all_days
    else:
        return False

# POST preOTs by a length of days
def preOT(s, access_token, ot_len, reason, method):
    check_days = ot_len_to_day(ot_len)
    if check_days:
        week_results = []
        for check_day in check_days:
            day_data = preOT_by_day(s, access_token, check_day, reason, method)
            week_results.append(day_data)
        print week_results
        return week_results
    else:
        return False
    