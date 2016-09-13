# -*- coding: utf-8 -*-

from flask import Flask
from headers import Headers
import requests
from lxml import etree
import simplejson
from selenium import webdriver
from urllib import urlencode
from urllib import quote

app = Flask(__name__)


@app.route('/')
def hello_world():
    print('hello world!')
    return 'hello world!'


@app.route('/keyword/<keyword>')
def main(keyword):
    ret = go_search(keyword)
    return ret


def go_search(keyword):
    keyword = quote(keyword.encode('utf8'))
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
    cap = webdriver.DesiredCapabilities.PHANTOMJS
    cap['phantomjs.page.customHeaders.Referer'] = headers['Referer']
    cap['phantomjs.page.settings.userAgent'] = headers['User-Agent']
    cap['phantomjs.page.settings.resourceTimeout'] = '1000'
    driver = webdriver.PhantomJS(service_args=['--load-images=no'], desired_capabilities=cap)
    driver.set_window_size(800, 600)
    driver.get(url)
    html = driver.page_source
    print(111)
    print(html)
    driver.close()
    # req = requests.get(url, headers=headers, timeout=60)
    if True:
        # html = req.text
        selector = etree.HTML(html)
        content_objs = selector.xpath('//div[@class="bk_entity_main"]/*')
        content_main = []
        content_side = []
        # print(etree.tostring(content_objs[0], encoding='utf8', method="html"))
        for content_obj in content_objs:
            content_string = etree.tostring(content_obj, encoding='utf8', method="html")
            content_main.append(content_string)
        side_one_objs = selector.xpath('//div[@id="sidebar_attr"]')
        side_two_objs = selector.xpath('//div[@id="sidebar_rel"]')
        side_one_string = ''
        side_two_string = ''
        if len(side_one_objs) > 0:
            side_one_obj = side_one_objs[0]
            side_one_string = etree.tostring(side_one_obj, encoding='utf8', pretty_print=True)
        if len(side_two_objs) > 0:
            side_two_obj = side_two_objs[0]
            side_two_string = etree.tostring(side_two_obj, encoding='utf8', pretty_print=True)

        content_side.append(side_one_string)
        content_side.append(side_two_string)
        ret['data']['main'] = content_main
        ret['data']['side'] = content_side
        ret['code'] = 1001
        ret['msg'] = 'success'

    return simplejson.dumps(ret)


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=37211, use_reloader=True)
