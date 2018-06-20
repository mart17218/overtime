# -*- coding: utf-8 -*-
# define constants

# smart office ip
smart_office_ip = '172.18.67.117'

# smart office url used
smart_office_base_url = 'http://' + smart_office_ip + '/foxconn'

# basic headers used in smart office request
basic_headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': '172.18.67.117',
    'Origin': 'http://' + smart_office_ip,
    'Pragma': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

# the overtime start at workday
default_workday_overtime_start = '18:30'

# the overtime end at workday
default_workday_overtime_end = '22:30'

# the overtime start at holiday
default_holiday_overtime_start = '9:30'

# the overtime end at holiday
default_holiday_overtime_end = '18:30'

# morning utf-8 decode: \xe4\xb8\x8a\xe5\x8d\x88
morning_keyword = '\xe4\xb8\x8a\xe5\x8d\x88'

# evening utf-8 decode: \xe4\xb8\x8b\xe5\x8d\x88
evening_keyword = '\xe4\xb8\x8b\xe5\x8d\x88'

# api url may have "test"...
is_test = False

CONSTANTS = None

def set_const(key, value):
    if not key in CONSTANTS:
        return False
    else:
        CONSTANTS[key] = value
        return True

def export():
    CONSTANTS = {
        'smart_office_base_url': smart_office_base_url,
        'basic_headers': basic_headers,
        'default_workday_overtime_start': default_workday_overtime_start,
        'default_workday_overtime_end': default_workday_overtime_end,
        'default_holiday_overtime_start': default_holiday_overtime_start,
        'default_holiday_overtime_end': default_holiday_overtime_end,
        'morning_keyword': morning_keyword,
        'evening_keyword': evening_keyword,
        'is_test': is_test
    }
    return CONSTANTS