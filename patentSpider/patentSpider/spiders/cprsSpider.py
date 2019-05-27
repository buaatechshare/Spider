# -*- coding: utf-8 -*-
import scrapy
import logging
import re
import json
from  scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import PatentspiderItem
from urllib.parse import urlparse, parse_qs
import urllib


class CpsrspiderSpider(CrawlSpider):
    name = 'cprsSpider'
    # start_urls = ['https://xueshu.baidu.com/s?wd=%E7%8A%81%E5%9C%B0&pn=0&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&filter=sc_type%3D%7B5%7D&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&bcp=2&sc_hit=1']

    start_urls = ['https://xueshu.baidu.com/s?wd=%E6%9C%BA%E6%A2%B0&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&usm=1&filter=sc_type%3D%7B5%7D&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&bcp=2&sc_hit=1']
    baidu_link = LinkExtractor(allow=("[\s\S]*.xueshu.baidu.com/s\?wd[\s\S]*&pn=[\s\S]*"))
    cprs_link = LinkExtractor(allow=("[\s\S]*.cprs.patentstar.com.cn[\s\S]*"))

    rules = {
        Rule(baidu_link,callback='baidu_parse',follow=True),
    }


    def baidu_parse(self, response):
        '//*[@id="16"]/div[1]/div[3]/div/span[6]/a'
        patent_urls = response.xpath("//div[@class='sc_allversion']//a[@title='cprs.patentstar.com.cn']//@href").extract()
        # logging.info(type(patent_urls))
        #print("patent_url:",patent_url)
        next_pages = response.xpath("//*[@id='page']/a[i[@class='c-icon-pager-next']]/@href").extract()
        #print("next:",next_pages)
        if len(patent_urls):
            for patent_url in patent_urls:
                ANE = patent_url.replace('\r\n','')
                ANE = re.findall('ANE=[\s\S]*',ANE)[0]
                ANE = ANE.replace('ANE=','')
                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
                # print("ANE:",ANE)
                # logging.info("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
                yield scrapy.Request(url='http://cprs.patentstar.com.cn/Search/GetPatentByAN?ANE='+ANE,method='GET',headers=headers,callback=self.cprs_parse)
        if next_pages:
           #next_pages = response.urljoin(next_pages)
            next_pages ='https://xueshu.baidu.com' +next_pages[0]
           # print('fxxk:',next_pages)
            yield scrapy.Request(next_pages, callback=self.baidu_parse)
    def cprs_parse(self, response):
        item = json.loads(response.text)["Data"]
        yield item
