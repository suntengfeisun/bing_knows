# -*- coding: utf-8 -*-

from selenium import webdriver



url = 'https://cn.bing.com/knows/search?intlF=0&q=%E5%88%98%E5%BE%B7%E5%8D%8E&FORM=HDRSC7&mkt=zh-cn'
url = 'http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word=%E5%88%98%E5%BE%B7%E5%8D%8E#z=0&pn=&ic=0&st=-1&face=0&s=0&lm=-1'
driver = webdriver.PhantomJS(service_args=['--load-images=no'])
driver.get(url)
print(url)
# elem = driver.find_element_by_xpath("//*")
# source_code = elem.get_attribute("outerHTML")
# print(source_code)

html = driver.execute_script("return document.body.outerHTML")
print html

content_objs = driver.find_elements_by_xpath('//a[@name="pn0"]/img')
print(content_objs[0].get_attribute('outerHTML'))
driver.quit()


