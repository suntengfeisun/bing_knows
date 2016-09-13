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


def get_baiduzhidao(keyword):
    ret = {
        'code': 1002,
        'msg': 'failure',
        'data': {}
    }
    try:
        url = 'http://zhidao.baidu.com/question/%s.html' % (keyword)
        headers = Headers.getHeaders()
        # req = requests.get(url, headers=headers, timeout=30)
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
        req.encoding = 'gbk'
        html = req.text.encode(encoding="utf-8", errors="ignore").decode("utf-8", errors="ignore")
        selector = etree.HTML(html)
        question = {
            'title': '',
            'author': '',
            'content': '',
            'time': ''
        }
        """
        处理提问
        """
        question_selectors = selector.xpath('//div[@id="wgt-ask"]')
        if len(question_selectors) > 0:
            question_selector = question_selectors[0]
            titles = question_selector.xpath('h1[1]/descendant::text()')
            author_times = question_selector.xpath('div[@id="ask-info"]/descendant::text()')
            contents = question_selector.xpath('pre[@accuse="qContent"]/text()')
            for title in titles:
                if title != '\n':
                    if question['title'] == '':
                        question['title'] = question['title'] + title
                    else:
                        question['title'] = question['title'] + '\n' + title
            for content in contents:
                if content != '\n':
                    if question['content'] == '':
                        question['content'] = question['content'] + content
                    else:
                        question['content'] = question['content'] + '\n' + content
            for author_time in author_times:
                if author_time != '\n' and author_time != u'分享' and author_time != '|':
                    if question['time'] == '':
                        question['time'] = (question['time'] + author_time).replace('\n', '')
                    else:
                        question['author'] = (question['author'] + author_time).replace('\n', '')
            # print(question['content'])

            """
            处理回答
            """
            anwser = deal_anwser(html, selector)
            """
            处理更多
            """
            more = []
            more_selectors = selector.xpath('//ul[@class="list-34 related-ul"]/li/a')
            for more_selector in more_selectors:
                urls = more_selector.xpath('@href')
                titles = more_selector.xpath('descendant::text()')
                if len(urls) > 0 and len(titles) > 0:
                    url_status = re.search(r'question/(.*?).html', urls[0], re.M | re.I)
                    if url_status:
                        url = re.search(r'question/(.*?).html', urls[0], re.M | re.I).group(1)
                        title = ''
                        for t in titles:
                            if t == '\n':
                                break
                            title = title + t
                        more.append({'url': url, 'title': title})
            ret['code'] = 1001
            ret['msg'] = 'success'
            ret['data'] = {
                'question': question,
                'anwser': anwser,
                'more': more
            }
    except:
        pass
    return simplejson.dumps(ret)


def deal_anwser(html, selector):
    anwser = {
        'title': '',
        'author': '',
        'content': '',
        'time': ''
    }
    if u'网友采纳' in html:
        # 584650945092901285
        # 585444949329229365
        anwser_selectors = selector.xpath('//div[contains(@id,"recommend-answer")]')
        if len(anwser_selectors) > 0:
            anwser_selector = anwser_selectors[0]
            title_times = anwser_selector.xpath('div[1]/descendant::text()')
            contents = anwser_selector.xpath(
                    'div[2]/div[@class="line content"]/descendant::*[@accuse="aContent"]/descendant::text()')
            authors = anwser_selector.xpath('descendant::a[@class="user-name"]/text()')
            for title_time in title_times:
                if title_time != '\n':
                    if anwser['time'] == '':
                        anwser['time'] = title_time.replace('\n', '')
                    else:
                        anwser['title'] = title_time
            for content in contents:
                if content != '\n':
                    if anwser['content'] == '':
                        anwser['content'] = anwser['content'] + content.replace(u'百度', '')
                    else:
                        anwser['content'] = anwser['content'] + '\n' + content.replace(u'百度', '')
            for author in authors:
                anwser['author'] = author.replace('\n', '')
            print(anwser['content'])
    elif u'提问者采纳' in html:
        # 195180529
        anwser_selectors = selector.xpath('//div[contains(@id,"best-answer")]')
        if len(anwser_selectors) > 0:
            anwser_selector = anwser_selectors[0]
            title_times = anwser_selector.xpath('div[1]/descendant::text()')
            contents = anwser_selector.xpath('div[2]/div[2]/descendant::text()')
            authors = anwser_selector.xpath('div[2]/div[1]/text()')
            for title_time in title_times:
                if title_time != '\n':
                    if anwser['time'] == '':
                        anwser['time'] = title_time.replace('\n', '')
                    else:
                        anwser['title'] = title_time
            for content in contents:
                if u'提问者评价' in content:
                    break
                if content != '\n' and content != u'分享' and content != u'评论' and content != '|':
                    if anwser['content'] == '':
                        anwser['content'] = anwser['content'] + content.replace(u'百度', '')
                    else:
                        anwser['content'] = anwser['content'] + '\n' + content.replace(u'百度', '')
            for author in authors:
                anwser['author'] = author.replace('\n', '')
            if anwser['author'] == '':
                authors = anwser_selector.xpath('div[3]/descendant::p/a[1]/text()')
                for author in authors:
                    if author != '\n':
                        anwser['author'] = author.replace('\n', '')
            print(anwser['content'])
    elif u'专业回答' in html:
        # 521898807444506485
        anwser_selectors = selector.xpath('//div[contains(@id,"wgt-quality")]')
        if len(anwser_selectors) > 0:
            anwser_selector = anwser_selectors[0]
            anwser['title'] = u'专业回答'
            contents = anwser_selector.xpath('div[3]/div[1]/descendant::text()')
            author_times = anwser_selector.xpath('div[2]/descendant::text()')
            for author_time in author_times:
                if author_time != '\n':
                    if anwser['author'] == '':
                        anwser['author'] = author_time.replace('\n', '')
                    else:
                        anwser['time'] = author_time.replace('\n', '')
            for content in contents:
                if content != '\n':
                    if anwser['content'] == '':
                        anwser['content'] = anwser['content'] + content.replace(u'百度', '')
                    else:
                        anwser['content'] = anwser['content'] + '\n' + content.replace(u'百度', '')
    elif u'最佳答案' in html:
        # 521898807444506485
        anwser_selectors = selector.xpath('//div[contains(@class,"wgt-best mod-shadow")]')
        if len(anwser_selectors) > 0:
            anwser_selector = anwser_selectors[0]
            anwser['title'] = u'最佳答案'
            contents = anwser_selector.xpath('div[2]/div[2]/descendant::text()')
            author_times = anwser_selector.xpath('div[1]/descendant::text()')
            authors = anwser_selector.xpath('div[3]/div[1]/div[2]/p[1]/a[1]/text()')
            for author in authors:
                anwser['author'] = author.replace('\n', '')
            for author_time in author_times:
                anwser['time'] = author_time.replace('\n', '')
            for content in contents:
                if content != '\n':
                    if anwser['content'] == '':
                        anwser['content'] = anwser['content'] + content.replace(u'百度', '')
                    else:
                        anwser['content'] = anwser['content'] + '\n' + content.replace(u'百度', '')
    else:
        anwser_selectors = selector.xpath('//div[contains(@id,"recommend-answer")]')
        if len(anwser_selectors) > 0:
            anwser_selector = anwser_selectors[0]
            title_times = anwser_selector.xpath('div[1]/descendant::text()')
            contents = anwser_selector.xpath('div[2]/div[@class="line content"]/pre[1]/descendant::text()')
            authors = anwser_selector.xpath('descendant::a[@class="user-name"]/text()')
            for title_time in title_times:
                if title_time != '\n':
                    if anwser['time'] == '':
                        anwser['time'] = title_time.replace('\n', '')
                    else:
                        anwser['title'] = title_time
            for content in contents:
                anwser['content'] = content
            for author in authors:
                anwser['author'] = author.replace('\n', '')
    return anwser
