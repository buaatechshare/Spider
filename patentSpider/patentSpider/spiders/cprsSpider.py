# -*- coding: utf-8 -*-
import scrapy
import re
from  scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from patentSpider.items import PatentspiderItem
from urllib.parse import urlparse, parse_qs


class CpsrspiderSpider(CrawlSpider):
    name = 'cprsSpider'
    start_urls = ['https://xueshu.baidu.com/s?wd=X%E5%B0%84%E7%BA%BF&pn=0&tn=SE_baiduxueshu_c1gjeupa&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&sc_hit=1&bcp=2&ie=utf-8&filter=sc_type%3D%7B5%7D']

    #start_urls = ['https://xueshu.baidu.com/s?wd=%E6%9C%BA%E6%A2%B0&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&usm=1&filter=sc_type%3D%7B5%7D&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&bcp=2&sc_hit=1']
    baidu_link = LinkExtractor(allow=("[\s\S]*.xueshu.baidu.com/s?wd[\s\S]*&pn=[\s\S]*"))
    cprs_link = LinkExtractor(allow=("[\s\S]*.cprs.patentstar.com.cn[\s\S]*"))

    rules = {
        Rule(baidu_link,callback='baidu_parse',follow=True),
        Rule(cprs_link,callback='cprs_parse',follow=False)
    }


    def baidu_parse(self, response):
        patent_url = response.xpath("//div[@id='1']//div[@class='sc_allversion']//a[@title='cprs.patentstar.com.cn']//@href").extract()
        if patent_url.__len__() > 0:
            ANE = patent_url[0].replace('\r\n','')
            ANE = re.findall('ANE=[\s\S]*',ANE)[0]
            ANE = ANE.replace('ANE=','')
            print("ANE:",ANE)
            yield scrapy.FormRequest(url='http://cprs.patentstar.com.cn/Search/GetPatentByAN',formdata={'ANE':ANE},callback=self.cprs_parse)
        next_pages= response.xpath("//*[@id='page']/a[i[@class='c-icon-pager-next']]/@href").extract_first()
        print("nxt:",next_pages)
        if next_pages:
            next_pages=response.urljoin(next_pages)
            yield scrapy.Request(next_pages,callback=self.baidu_parse)
    def cprs_parse(self, response):
        item = PatentspiderItem()
        item['title']=response.text
        #item抓取  by xzy
        # title= response.xpath("//label[@class='title-color']").extract()
        # print("title_out:",title)
        # if title.__len__() > 0:
        #     item['title'] = title[0]
        # applicationNo = response.xpath("//div[@class='item-content fl']/div[1]/span/text").extract()
        # print("AN_out:",applicationNo)
        # if applicationNo.__len__() > 0:
        #     item['AN'] = applicationNo[0]
        # primaryClass = response.xpath("//div[@class='item-content fl']/div[8]//span/text").extract()
        # print("MC_out:",primaryClass)
        # if primaryClass.__len__() > 0:
        #     item['MC'] = primaryClass[0]

        # item['title']=response.text
        # print('data:',response.data)
        # print("response:",str(response.body,encoding='utf8'))
        # item = PatentspiderItem()
        # title= response.xpath("//label[@class='title-color']").extract()
        # print("title_out:",title)
        # if title.__len__() > 0:
        # item['title'] = title[0]
        # applicationNo = response.xpath("//div[@class='item-content fl']/div[1]/span").extract()
        # if applicationNo.__len__() > 0:
        # item['applicationNo'] = applicationNo[0]
        # primaryClass = response.xpath("//div[@class='item-content fl']/div[8]//span").extract()
        # if primaryClass.__len__() > 0:
        #     item['primaryClass'] = primaryClass[0]
        # print("item:")
        #

        # print(item)
        yield item
