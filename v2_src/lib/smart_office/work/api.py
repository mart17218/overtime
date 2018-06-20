# -*- coding: utf-8 -*-
# smart office work api
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

# api related to work
get_on_time_log = smart_office_base_url + '/AppOnTimev3/services/GetByUserRange.ashx'
get_attenance_url = smart_office_base_url + '/AppOnTimev3/services/GetByUserRange.ashx'
get_abnormal_url = smart_office_base_url + '/AppOnTimev3/services/GetUserAbnormalData.ashx'

# extract "work lsit" data
def extract_abnormal_data(abd):
    e_data = {
        'id': abd['docnum'],
        'date': abd['date'],
        'type': abd['type'], # short2 = 'leave' / 'arrive' miss
        'arrive': abd['arrive'],
        'leave': abd['leave'],
        'status': abd['status']
    }
    return e_data

# extract "attenance list" data
def extract_attenance_data(abd):
    e_data = {
        "date": abd['date'],
        "arrive": abd['arrive'],
        "leave": abd['leave'],
        "status": abd['status'],
        "work_hour": abd['work_hour']
    }
    return e_data

# get the work list
def get_work_list(s, access_token, query_date_start, query_date_end):
    query_data = {
        'StartDate':query_date_start.strftime('%Y/%m/%d'),
        'EndDate':query_date_end.strftime('%Y/%m/%d')
    }
    res = s.get(get_on_time_log, params = query_data)
    # print res.text
    try:
        work_data = map(lambda data: \
            {
            'date': data['date'].replace('/', '-'),
            'arrive': data['arrive'],
            'leave': data['leave'],
            'work_hour': data['work_hour'],
            'remark': data['remark']
            }, common.dic_text_to_dic(res.text)['data'])
        return work_data
    except:
        return []

# get the abnormal work list
def get_abnormal_list(s, access_token, query_date_start, query_date_end):
    query_data = {
        'sort': 'date',
        'StartDate': query_date_start.strftime('%Y/%m/%d'),
        'EndDate': query_date_end.strftime('%Y/%m/%d'),
    }
    get_abnormal_res = s.get(get_abnormal_url, params = query_data)
    abnormal_res_data = common.dic_text_to_dic(get_abnormal_res.text)['data']
    extracted_data = map(extract_abnormal_data, abnormal_res_data)
    return extracted_data

# get the attendance list
def get_attendance_list(s, access_token, query_date_start, query_date_end):
    query_data = {
        'StartDate': query_date_start.strftime('%Y/%m/%d'),
        'EndDate': query_date_end.strftime('%Y/%m/%d')
    }
    get_attenance_res = s.get(get_attenance_url, params = query_data)
    attenance_res_data = common.dic_text_to_dic(get_attenance_res.text)['data']
    extracted_data = map(extract_attenance_data, attenance_res_data)
    return extracted_data