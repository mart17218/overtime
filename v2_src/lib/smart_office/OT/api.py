# -*- coding: utf-8 -*-
# smart office OT api
import re
import math
import random
import requests
import datetime
from time import sleep
from bs4 import BeautifulSoup as bs
from ..utils import constants, common, general
from ..preOT import api as preOT_api
from ..work import api as work_api

# consatns included
CONSTANTS = constants.export()
smart_office_base_url = CONSTANTS['smart_office_base_url']

# format: { <username1>: { <date1>: <job1>, <date2>: <job2>, ... }, <username2>: ... }
OT_schedule = {}

# format: { <username1>: <password1>, <username2>: <password2>, ... }
OT_preserved_data = {}

# this is the file that preserved the schedule
preserved_file = './OT_schedule.sl'

# api related to OT
if CONSTANTS['is_test']:
    get_preOT_list_url = smart_office_base_url + '/overtime_test/service/QueryOTCUser.ashx'
    OT_url = smart_office_base_url + '/overtime_test/NewOT.aspx'
    get_total_ot_hours = smart_office_base_url + '/overtime_test/service/SumOTCUserHours.ashx'
else:
    get_preOT_list_url = smart_office_base_url + '/overtime/service/QueryOTCUser.ashx'
    OT_url = smart_office_base_url + '/overtime/NewOT.aspx'
    get_total_ot_hours = smart_office_base_url + '/overtime/service/SumOTCUserHours.ashx'

# get the OT list
def get_OT_list(s, access_token, query_date_start, query_date_end):
    query_data = {
        'sotdate':query_date_start.strftime('%Y-%m-%d'),
        'eotdate':query_date_end.strftime('%Y-%m-%d'),
        'userinfo':'',
        'sstatus':'',
        'smethods':'',
        'curpagenum':'0',
        'processdate':'',
        'actpre':'實報'
    }
    res = s.post(get_preOT_list_url, data = query_data, params = {'access_token': access_token})
    res = s.post(get_preOT_list_url, data = query_data, params = {'access_token': access_token})
    # print res.text
    try:
        OT_data = map(lambda data: \
            {
                'date': common.specail_date_format_to_date(data['STARTTIME']),
                'desc': data['OTDESC'].decode('utf8'),
                'method': data['METHODS'].decode('utf8'),
                'from': common.specail_date_format_to_time(data['STARTTIME']),
                'to': common.specail_date_format_to_time(data['ENDTIME']),
                'pre_ot_id': data['PREOTNO'],
                'status': data['DOCSTATUS'].decode('utf8'),
            }, common.dic_text_to_dic(res.text))
        return OT_data
    except:
        return []

# get ot hour by a time range
def get_ot_hours(s, access_token, query_date_start, query_date_end):
    query_data = {
        'sotdate': query_date_start.strftime('%Y-%m-%d'),
        'eotdate': query_date_end.strftime('%Y-%m-%d'),
        'userinfo': '',
        'sstatus': '',
        'smethods': '',
        'curpagenum': '0',
        'processdate': '',
        'actpre': '實報'
    }
    res = s.post(get_total_ot_hours, data = query_data, params = {'access_token': access_token})
    total_hour, total_num = res.text.split('^')
    return {'total_hour': total_hour, 'total_num': total_num}

# combine preOT, OT and work data at a day
def get_all_data_by_day(s, access_token, date, day_type = 'workday'):
    now = datetime.datetime.now()
    # Today
    if date.date() == now.date():
        return False
    this_pre_ot = preOT_api.get_preOT_list(s, access_token, date, date)
    this_ot = get_OT_list(s, access_token, date, date)
    this_work = work_api.get_work_list(s, access_token, date, date)
    # No preOT or no work history
    if not len(this_work):
        print 'No work history data'
        return False
    if not len(this_pre_ot):
        print 'No preOT data'
        return False
    # work time < 8 hours when 'workday'
    try:
        leave_time = datetime.datetime.strptime(this_work[0]['leave'], '%H:%M')
        arrive_time = datetime.datetime.strptime(this_work[0]['arrive'], '%H:%M')
        if (day_type is 'workday') and (leave_time - arrive_time < datetime.timedelta(hours=8)):
            return False
    except Exception as e:
        # wrong time format
        print e
        pass       
    # preOT exists but not available
    if this_pre_ot[0]['status'].encode('utf8') != '\xe5\xb7\xb2\xe7\x94\x9f\xe6\x95\x88':
        return False
    return {'pre': this_pre_ot, 'ot': this_ot, 'work': this_work}

# POST a OT at a day
def OT_by_day(s, access_token, all_data):
    # ot
    if not all_data:
        return False
    elif (len(all_data['pre']) and (not len(all_data['ot'])) and len(all_data['work'])):
        print 'Start OT'
        pre_data = all_data['pre'][0]
        work_data = all_data['work'][0]
        final_arrive_time = max(work_data['arrive'], pre_data['arrive'])
        final_leave_time = min(work_data['leave'], pre_data['leave'])
        OT_arrive = common.formal_time_str_to_special_format(final_arrive_time)
        OT_leave = common.formal_time_str_to_special_format(final_leave_time)
        res_service_OT = s.get(OT_url, params = {'access_token': access_token})
        soup = bs(res_service_OT.text)
        post_OT_body = {
            '__WORKFLOWTARGET': 'apsoft.workflow.client.workflow',
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': 'Approve',
            '__VIEWSTATE': soup.select('#__VIEWSTATE')[0]['value'],
            '__EVENTVALIDATION': soup.select('#__EVENTVALIDATION')[0]['value'],
            '__WORKFLOWSTATE': soup.select('#__WORKFLOWSTATE')[0]['value'],
            '__COMMENT': '',
            '__WORKFLOWSEARCH': '',
            'PreOTNo': pre_data['pre_ot_id'],
            'Prehrs6': pre_data['hrs6'],
            'fsdate': pre_data['date'],
            'fstime': OT_arrive,
            'fedate': pre_data['date'],
            'fetime': OT_leave,
            'frestmin': '0',
            'fdesc': pre_data['desc'],
            'fmethods': pre_data['method'],
            'skey': '',
            'Prekey': ''
        }
        res_post_OT = s.post(OT_url, data = post_OT_body, headers = {'Referer': smart_office_base_url + '/overtime/overtime.aspx'}, params = {'access_token': access_token})
        print common.dic_text_to_dic(res_post_OT.text)
        new_workflow_state = common.dic_text_to_dic(res_post_OT.text)['data']['workflowstate']
        post_OT_body['__WORKFLOWSTATE'] = new_workflow_state
        res_second_post_OT = s.post(OT_url, data = post_OT_body, headers = {'Referer': OT_url}, params = {'access_token': access_token})
        print common.dic_text_to_dic(res_second_post_OT.text)
        return res_second_post_OT.text
    else:
        return False

# function to handle "ot_len"
def ot_len_to_day(ot_len):
    now_day = datetime.datetime.now()
    if now_day.strftime('%w') is '1':
        last_work_day = now_day - datetime.timedelta(days = 3)
    else:
        last_work_day = now_day - datetime.timedelta(days = 1)
    if ot_len is 'd':
        return [{ 'day': last_work_day, 'type': 'workday' }]
    elif ot_len is 'sat':
        to_last_saturday = 6 - int(now_day.strftime('%w')) - 7
        last_saturday = now_day + datetime.timedelta(days = to_last_saturday)
        return [{ 'day': last_saturday, 'type': 'holiday' }]
    elif ot_len is 'sun':
        to_last_sunday = 7 - int(now_day.strftime('%w')) - 7
        last_sunday = now_day + datetime.timedelta(days = to_last_sunday)
        return [{ 'day': last_sunday, 'type': 'holiday' }]
    elif ot_len is 'w':
        all_days = []
        for day in range(int(last_work_day.strftime('%w')) + 8):
            all_days.append({ 'day': last_work_day - datetime.timedelta(days = day), 'type': 'workday' })
        return all_days
    else:
        return False

# POST OTs by a length of days
def OT(s, access_token, ot_len):
    check_days = ot_len_to_day(ot_len)
    if check_days:
        week_results = []
        for check_day in check_days:
            day_data = get_all_data_by_day(s, access_token, check_day['day'], check_day['type'])
            week_results.append(OT_by_day(s, access_token, day_data))
        return week_results
    else:
        return False
    
# init. OT schedules...
def load_schedule():
    with open(preserved_file, 'r') as f:
        for line in f.readlines():
            username, encrypt_pass, day_ordinal = line.split(',')
            password = general.decrypt(encrypt_pass)
            OT_preserved_data[username] = password
            day_ordinal = int(day_ordinal)
            schedule_config = {
                'username': username, 
                'password': password,
                'day': datetime.datetime.fromordinal(day_ordinal)
            }
            job = general.schedule_job(schedule_one_day_OT, schedule_config)
            if OT_schedule.get(username):
                OT_schedule[username][day_ordinal] = job
            else:
                OT_schedule[username] = {
                    day_ordinal: job
                }

# preserver the schedule data
def keep_schedule():
    print 1
    with open(preserved_file, 'w') as f:
        print 2
        for username in OT_schedule:
            print 3
            for day_ordinal in OT_schedule[username]:
                print 4
                encrypt_pass = general.encrypt(OT_preserved_data[username])
                format_record = '{0},{1},{2}'.format(username, encrypt_pass, day_ordinal)
                print format_record
                f.write(format_record + '\n')
            
    
# clear the OT_schedule
def clear_OT_schedule(username, day):
    general.cancel_job(OT_schedule[username][day.toordinal()])
    del OT_schedule[username][day.toordinal()]
    if not OT_schedule[username]:
        del OT_schedule[username]
    return

# query schedule
def get_OT_schedule(username):
    if OT_schedule.get(username):
        dates = map(lambda x: datetime.datetime.fromordinal(x), OT_schedule[username])
        return map(lambda x: datetime.datetime.strftime(x, '%Y-%m-%d'), dates)
    else:
        return []

# determine whether the schedule job is success or not
def schedule_OT_callback(schedule_config):
    if not schedule_config:
        return False
    else:
        # clear timer and schedule_config
        clear_OT_schedule(schedule_config['username'], schedule_config['day'])
        return True

# implement the "schedule OT" callback
def schedule_one_day_OT(schedule_config):
    print schedule_config['username'] + ' do schedule' + ' at ' + str(schedule_config['day'])
    now = datetime.datetime.now()
    if schedule_config['day'] > now:
        # the "day" is later than now, skip this schedule
        print 'OT in the future...'
        return False
    if (now - schedule_config['day']).total_seconds() > 15*24*60*60:
        # 15 days ahead from now, may be some error...
        return False
    s = requests.Session()
    s.headers.update(CONSTANTS['basic_headers'])
    login_res = general.login(s, schedule_config['username'], schedule_config['password'])
    if not login_res:
        # Not able to LOGIN, cancel job...
        # [TODO] Retry, notify...
        print 'Login failed...'
        return schedule_config
    else:
        access_token = general.get_access_token(s)
        weekday = int(schedule_config['day'].strftime('%w'))
        if weekday is 6 or weekday is 0:
            day_type = 'holiday'
        else:
            day_type = 'weekday'
        all_data = get_all_data_by_day(s, access_token, schedule_config['day'], day_type)
        if len(all_data['ot']):
            # already done OT
            print 'Already OT!!'
            return schedule_config
        else:
            result = OT_by_day(s, access_token, all_data)
            if result:
                # success OT
                print 'OT successfully'
                return schedule_config
            else:
                # waiting for the next day
                print 'Not available...'
                return False

# preserved_req should be the request from preOT
def schedule_OT(data, days = None):
    if not days:
        days = preOT_api.ot_len_to_day(data['type'])
    OT_preserved_data[data['username']] = data['password']
    for day in days:
        schedule_config = {
            'username': data['username'], 
            'password': data['password'],
            'day': day
        }
        job = general.schedule_job(schedule_one_day_OT, schedule_config, schedule_OT_callback)
        if OT_schedule.get(data['username']):
            OT_schedule[data['username']][day.toordinal()] = job
        else:
            OT_schedule[data['username']] = {
                day.toordinal(): job
            }
    return OT_schedule