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
    # queries=['IP','机械','X射线','数字电路','电气','器件','通信','光电子','图像','广播电视']
    # start_urls = ['https://xueshu.baidu.com/s?wd=%E6%9C%BA%E6%A2%B0&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&usm=1&filter=sc_type%3D%7B5%7D&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&bcp=2&sc_hit=1']
    queries = ['IP','计算机专业','器件','通信','空间信息','汇编','程序设计','微机','办公自动化','集成电路',
               '设备','计算机软件','技术','多媒体','安全','光','信息工程','计算机病毒','传感器','操作系统',
               '应用软件','科技','软件测试','计算机技术','媒体','广域网','网络','局域网','Linux','信息技术',
               '信息','一系列','数据结构','微电子','算法','Java','自动化','入侵','电子商务','硬件',
               '信号','计算机控制','网络工程','数字电路','电脑','并行','单片机','软件','光电','信息处理',
               '通信工程','TCP','通讯','计算机科学','自然语言','电子线路','广播电视','电气','集成系统','网络系统',
               'IT','软件工程','电子信息','信息科学','智能科学','科学技术','光电子','图像','计算机网络','接口技术',
               '信号处理','密码学','网络管理','电气工程','数据库','信息安全','功能化','信息管理','数据处理','微电子学',
               '电子设备']
    def start_requests(self):
        start_urls=[]
        for query in self.queries:
            start_urls.append('https://xueshu.baidu.com/s?wd='+query+'&pn=0&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&filter=sc_type%3D%7B5%7D&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&bcp=2&sc_hit=1')
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.baidu_parse)
    baidu_link = LinkExtractor(allow=("[\s\S]*.xueshu.baidu.com/s\?wd[\s\S]*&pn=[\s\S]*"))
    cprs_link = LinkExtractor(allow=("[\s\S]*.cprs.patentstar.com.cn[\s\S]*"))

    rules = {
        Rule(baidu_link,callback='baidu_parse',follow=True),
    }

    

    def baidu_parse(self, response):
        # '//*[@id="16"]/div[1]/div[3]/div/span[6]/a'
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
          # next_pages = response.urljoin(next_pages)
            next_pages ='https://xueshu.baidu.com' +next_pages[0]  
            yield scrapy.Request(next_pages, callback=self.baidu_parse)
    def cprs_parse(self, response):
        item = json.loads(response.text)["Data"]
        yield item
