# -*- coding: utf-8 -*-
from flask import render_template, Flask, request, url_for, Response, jsonify, make_response
import re
import os
import math
import random
import requests
import datetime
import atexit
from time import sleep
from bs4 import BeautifulSoup as bs
from functools import wraps
import werkzeug.exceptions as ex

# include tools module
from lib.tools import api as tool_api

# include smart office modules
from lib.smart_office.utils import constants, common, general
from lib.smart_office.OT import api as OT_api
from lib.smart_office.preOT import api as preOT_api
from lib.smart_office.work import api as work_api

# include chinese chinese_poetry modules
from lib.chinese_poetry import api as poetry_api

# constants
CONSTANTS = constants.export()
ChangeLog_filename = 'ChangeLog.txt'

# flask app
app = Flask(__name__)

# error classes
# WrongUsernamePassword: exception code = 4001; http status code = 400
class WrongUsernamePassword(ex.HTTPException):
    code = 400
    description = 'Wrong Username/Password'

ex.default_exceptions[4001] = WrongUsernamePassword
abort = ex.Aborter()

# a wrapper, for common use for login check
def valid_login(api_method):
    @wraps(api_method)
    def check_valid_user_password(*args, **kwargs):
        s = requests.Session()
        s.headers.update(CONSTANTS['basic_headers'])
        data = common.dic_text_to_dic(request.data)
        login_res = general.login(s, data['username'], data['password'])
        if not login_res:
            abort(4001)
        else:
            access_token = general.get_access_token(s)
            return api_method(s, access_token, data, *args, **kwargs)
    return check_valid_user_password

# a wrapper, for api call logging
def log_api(api_method):
    @wraps(api_method)
    def log_api_to_console(*args, **kwargs):
        req_uri = request.path
        req_parameters = common.dic_text_to_dic(request.data)
        del req_parameters['username']
        del req_parameters['password']
        print req_uri
        print req_parameters
        return api_method(*args, **kwargs)
    return log_api_to_console

@app.route("/sentence", methods = ['GET'])
def sentence():
    try:
        sentence = poetry_api.random_a_sentence()
        return_sentence = sentence['author'] + ':\n' + sentence['sentence'] + '...'
        return Response(return_sentence.replace('u\'', '\'').replace('\'','"'), content_type="application/json;charset=UTF-8")
    except:
        return '(￣Д ￣)', 400

@app.route("/get_user", methods = ['POST'])
@valid_login
def get_user(s, access_token, data):
    now = datetime.datetime.now()
    days_from_now = (now - datetime.timedelta(days=1))
    result = general.get_user_info(s, access_token, days_from_now, now)
    return Response(common.utf_to_res_text(result), content_type="application/json;charset=UTF-8")

@app.route("/ot_list", methods = ['POST'])
@valid_login
@log_api
def get_OT(s, access_token, data):
    now = datetime.datetime.now()
    last_monday = now - datetime.timedelta(days=(int(now.strftime('%w')) + 13))
    result = OT_api.get_OT_list(s, access_token, last_monday, now)
    return Response(common.utf_to_res_text(result), content_type="application/json;charset=UTF-8")

@app.route("/pre_ot_list", methods = ['POST'])
@valid_login
@log_api
def get_preOT(s, access_token, data):
    now = datetime.datetime.now()
    last_monday = now - datetime.timedelta(days=(int(now.strftime('%w')) + 13))
    next_monday = last_monday + datetime.timedelta(days=21)
    result = preOT_api.get_preOT_list(s, access_token, last_monday, next_monday)
    return Response(common.utf_to_res_text(result), content_type="application/json;charset=UTF-8")

@app.route("/work_list", methods = ['POST'])
@valid_login
@log_api
def get_work(s, access_token, data):
    access_token = general.get_access_token(s)
    now = datetime.datetime.now()
    last_monday = now - datetime.timedelta(days=(int(now.strftime('%w')) + 6))
    result = work_api.get_work_list(s, access_token, last_monday, now)
    return Response(common.utf_to_res_text(result), content_type="application/json;charset=UTF-8")

@app.route("/ot_hour", methods = ['POST'])
@valid_login
def ot_hours(s, access_token, data):
    now = datetime.datetime.now()
    first_month_day = datetime.datetime(int(now.strftime('%Y')), int(now.strftime('%m')), 1)
    result = OT_api.get_ot_hours(s, access_token, first_month_day, now)
    return Response(common.utf_to_res_text(result), content_type="application/json;charset=UTF-8")

@app.route("/ot", methods = ['POST'])
@valid_login
@log_api
def get_ot_body(s, access_token, data):
    result = OT_api.OT(s, access_token, data['type'])
    if not result or not len(result):
        return 'Nothing changes', 400
    else:
        return str(len(result)), 200

@app.route("/pre", methods = ['POST'])
@valid_login
@log_api
def get_pre_ot_body(s, access_token, data):
    result = preOT_api.preOT(s, access_token, data['type'], data['reason'], data['method'])
    if not result or not len(result):
        return 'Nothing changes', 400
    else:
        return str(len(result)), 200

@app.route("/attendance_list", methods = ['POST'])
@valid_login
@log_api
def get_attendance(s, access_token, data):
    now = datetime.datetime.now()
    days_from_now = (now - datetime.timedelta(days=30))
    # attendance in 30 days
    result = work_api.get_attendance_list(s, access_token, days_from_now, now)
    return Response(common.utf_to_res_text(result), content_type="application/json;charset=UTF-8")

@app.route("/abnormal_list", methods = ['POST'])
@valid_login
@log_api
def get_abnormal(s, access_token, data):
    now = datetime.datetime.now()
    days_from_now = (now - datetime.timedelta(days=400))
    # abnormal in 400 days
    result = work_api.get_abnormal_list(s, access_token, days_from_now, now)
    return Response(common.utf_to_res_text(result), content_type="application/json;charset=UTF-8")

@app.route("/test", methods = ['POST'])
@valid_login
def test1(s, access_token, data):
    test_day = datetime.datetime.strptime(data['day'], '%Y-%m-%d') if data.get('day') else None
    result = OT_api.schedule_OT(data, [test_day])
    return Response(common.utf_to_res_text({'result': result}), content_type="application/json;charset=UTF-8")

@app.route("/test2", methods = ['POST'])
@valid_login
def test2(s, access_token, data):
    result = OT_api.get_OT_schedule(data['username'])
    return Response(common.utf_to_res_text({'result': result}), content_type="application/json;charset=UTF-8")

@app.route("/", methods = ['GET'])
def root():
    return render_template('index.html')

@app.route("/doc", methods = ['GET'])
def doc():
    return render_template('document.html')

@app.route("/seat", methods = ['GET'])
def seat():
    return render_template('seat.html')

# call on process start
def start():
    return

if __name__ == "__main__":
#    start()
    port = 23344
    app.run(host='0.0.0.0', port=port)
#    app.run(host='0.0.0.0', port=port, debug=True)
