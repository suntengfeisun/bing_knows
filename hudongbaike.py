# -*- coding: utf-8 -*-

import requests
from headers import Headers
from proxies import Proxies
import chardet
import sys
from lxml import etree
import simplejson
import re

reload(sys)
sys.setdefaultencoding('utf-8')


def get_hudongbaike(keyword):
    ret = {
        'code': 1002,
        'msg': 'failure',
        'data': []
    }
    url = 'http://www.baike.com/wiki/%s' % (keyword)
    headers = Headers.getHeaders()
    # req = requests.get(url, headers=headers, timeout=60)
    while True:
        proxies = Proxies.get_proxies()
        print(proxies)
        try:
            req = requests.get(url, headers=headers, timeout=60, proxies=proxies)
            status = True
        except:
            status = False
        if status:
            break
    if req.status_code == 200:
        data = []
        html = req.content
        # print(html)
        selector = etree.HTML(html)
        main_selectors = selector.xpath('//div[@class="l w-640"]')
        if len(main_selectors) > 0:
            main_selector = main_selectors[0]
            xpaths = [
                'div[@class="content-h1"]',
                'div[@class="place"]',
                'div[@id="unifyprompt"]',
                'div[@id="baikeguancha"]',
                'div[@id="datamodule"]',
                'div[@fieldset="catalog"]',
                'div[@id="content"]',
                'div[@class="content-h1"]'
            ]
            for xpath in xpaths:
                temp_selectors = main_selector.xpath(xpath)
                if len(temp_selectors) > 0:
                    temp_selector = temp_selectors[0]
                    data.append(etree.tostring(temp_selector, encoding='utf8', method="html"))
        ret['code'] = 1001
        ret['msg'] = 'success'
        ret['data'] = data
    return simplejson.dumps(ret)
