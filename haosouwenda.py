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


def get_haosouwenda(keyword):
    ret = {
        'code': 1002,
        'msg': 'failure',
        'data': {
            'question': {},
            'anwser': {},
            'more': {}
        }
    }
    url = 'http://wenda.so.com/q/%s' % (keyword)
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
        html = req.content
        selector = etree.HTML(html)
        question = anwser = {}
        more = []
        """
        处理问题
        """
        question_selectors = selector.xpath('//div[@ask_id="%s"]' % keyword)
        if len(question_selectors) > 0:
            question_selector = question_selectors[0]
            titles = question_selector.xpath('descendant::h2[@class="title js-ask-title"]/text()')
            authors = question_selector.xpath('descendant::a[contains(@class,"ask-author")]/text()')
            times = question_selector.xpath('descendant::div[@class="text"]/descendant::text()')
            contents = question_selector.xpath('descendant::div[@class="q-cnt"]/text()')

            title = content = author = time = ''
            if len(titles) > 0:
                title = titles[0]
            if len(authors) > 0:
                author = authors[0]
            if len(times) > 0:
                times.reverse()
                for t in times:
                    if '\n' not in t:
                        time = t
                        break
            if len(contents) > 0:
                content = contents[0]
            question = {
                'title': title,
                'content': content,
                'author': author,
                'time': time
            }

        """
        处理回答
        """
        anwser_selectors = selector.xpath('//div[@class="mod-resolved-ans js-form"]')
        if len(anwser_selectors) > 0:
            anwser_selector = anwser_selectors[0]
            title = u'满意答案'
            authors = anwser_selector.xpath('descendant::a[contains(@class,"ask-author")]/text()')
            times = anwser_selector.xpath('descendant::div[@class="text"]/descendant::text()')
            contents = anwser_selector.xpath('descendant::div[@class="resolved-cnt"]/descendant::text()')

            author = time = content = ''
            if len(authors) > 0:
                author = authors[0]
            if len(times) > 0:
                times.reverse()
                for t in times:
                    if '\n' not in t:
                        time = t
                        break
            if len(contents) > 0:
                for c in contents:
                    if content == '':
                        content = c
                    else:
                        content = content + '\n' + c
            anwser = {
                'title': title,
                'content': content,
                'author': author,
                'time': time
            }

        """
        处理更多
        """
        more_selectors = selector.xpath('//div[@id="ask-relate"]/descendant::li[@class="clearfix"]/a')
        for more_selector in more_selectors:
            urls = more_selector.xpath('@href')
            titles = more_selector.xpath('descendant::text()')
            if len(urls) > 0 and len(titles) > 0:
                url_status = re.search(r'q/(.*?)\?', urls[0], re.M | re.I)
                if url_status:
                    url = re.search(r'q/(.*?)\?', urls[0], re.M | re.I).group(1)
                    title = ''
                    for t in titles:
                        if t == '\n':
                            break
                        title = title + t
                    more.append({'url': url, 'title': title})
        ret['data'] = {
            'question': question,
            'anwser': anwser,
            'more': more
        }
        if len(ret['data']['question']) > 0:
            ret['code'] = 1001
            ret['msg'] = 'success'
    return simplejson.dumps(ret)
