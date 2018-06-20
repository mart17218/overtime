# -*- coding: utf-8 -*-
import math
import random
import requests
from time import sleep
from bs4 import BeautifulSoup as bs

base_shi_url = 'https://fanti.dugushici.com'

def random_a_sentence():
    try:
        t_1 = base_shi_url + '/ancient_proses/query?q%5Bprose_series_id_eq%5D=1'
        t_2 = base_shi_url + '/ancient_proses/query?q%5Bprose_series_id_eq%5D=16'
        t_3 = base_shi_url + '/ancient_proses/query?q%5Bprose_series_id_eq%5D=28'
        t_4 = base_shi_url + '/ancient_proses/query?q%5Bprose_series_id_eq%5D=5'
        types = [t_1, t_2, t_3, t_4]
        type_index = random.randint(0,3)
        select_type = types[type_index]
        res = requests.get(select_type)
        total_numbers = float(bs(res.text).select('.total_page')[0].select('span')[0].text)
        pages = int(math.ceil(total_numbers/10))
        page_index = random.randint(1, pages)
        select_result = requests.get(select_type + '&page=' + str(page_index))
        select_data = bs(select_result.text).select('table')[1].select('tr')[1:]
        select_data_index = random.randint(0, len(select_data)-1)
        select_data_url = select_data[select_data_index].select('td a')[0]['href']
        res = requests.get(base_shi_url + select_data_url)
        author = bs(res.text).select('div .sub a')[0].text.encode('utf8').strip()
        content = bs(res.text).select('.content')[0].text.encode('utf8').strip()
        print author
        print content
        sentences = filter(lambda s: len(s) > 0, content.split('\xe3\x80\x82'))
        sens_len = len(sentences)
        select_index = random.randint(0, sens_len-1)
        return {'author': author.decode('utf8'), 'sentence': sentences[select_index].strip().decode('utf8')}
    except Exception,e:
        print e
        return False