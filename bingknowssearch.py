# -*- coding: utf-8 -*-

import requests
import simplejson
from flask import Flask
from lxml import etree
from headers import Headers
from proxies import Proxies
from baiduzhidao import *
from hudongbaike import *
from haosouwenda import *

app = Flask(__name__)


@app.route('/')
def hello_world():
    print('hello world!')
    return 'hello world!'


@app.route('/hudongbaike/<keyword>')
def hudongbaike(keyword):
    ret = get_hudongbaike(keyword)
    return ret


@app.route('/baiduzhidao/<keyword>')
def baiduzhidao(keyword):
    ret = get_baiduzhidao(keyword)
    return ret


@app.route('/haosouwenda/<keyword>')
def haosouwenda(keyword):
    ret = get_haosouwenda(keyword)
    return ret


@app.route('/keyword/<keyword>')
def main(keyword):
    ret = go_search(keyword)
    return ret


def go_search(keyword):
    ret = {
        'code': 1002,
        'msg': 'failure',
        'data': {
            'main': [],
            'side': []
        }
    }
    url = 'https://cn.bing.com/knows/search?q=%s&mkt=zh-cn' % (keyword)
    headers = Headers.getHeaders()
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
        html = req.text
        selector = etree.HTML(html)
        content_objs = selector.xpath('//div[@class="bk_entity_main"]/*')
        content_main = []
        content_side = []
        if len(content_objs) > 0:
            print(etree.tostring(content_objs[0], encoding='utf8', method="html"))
            for content_obj in content_objs:
                content_string = etree.tostring(content_obj, encoding='utf8', method="html")
                content_main.append(content_string)
            side_one_objs = selector.xpath('//div[@id="sidebar_attr"]')
            side_two_objs = selector.xpath('//div[@id="sidebar_rel"]')
            side_one_string = ''
            side_two_string = ''
            if len(side_one_objs) > 0:
                side_one_obj = side_one_objs[0]
                side_one_string = etree.tostring(side_one_obj, encoding='utf8', method="html")
            if len(side_two_objs) > 0:
                side_two_obj = side_two_objs[0]
                side_two_string = etree.tostring(side_two_obj, encoding='utf8', method="html")

            content_side.append(side_one_string)
            content_side.append(side_two_string)
            ret['data']['main'] = content_main
            ret['data']['side'] = content_side
            ret['code'] = 1001
            ret['msg'] = 'success'

    return simplejson.dumps(ret)


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=3721, use_reloader=True, threaded=True)
