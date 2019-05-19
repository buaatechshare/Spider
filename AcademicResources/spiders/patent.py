# -*- coding: utf-8 -*-
import io

import requests
import scrapy
from scrapy_splash import SplashRequest, SplashJsonResponse

from AcademicResources.helpers import extract_text_by_css, convert_str_to_integer, str_to_datetime, \
    split_str_by_semicolon
from AcademicResources.items import PatentItem

default_script = """function main(splash)
    splash:init_cookies(splash.args.cookies)
    assert(splash:go(splash.args.url))
    assert(splash:wait(0.5))

    return {
        url = splash:url(),
        cookies = splash:get_cookies(),
        html = splash:html(),
    }
end"""


class PatentSpider(scrapy.Spider):
    name = 'patent'
    allowed_domains = ['cnki.net']

    # 深度学习 软件 大数据 计算机 编程 程序 电子 通信 多媒体 网络网页
    queries = ['IP', '计算机专业', '器件', '通信', '空间信息', '汇编', '程序设计', '微机', '办公自动化', '集成电路', '设备', '计算机软件', '技术', '多媒体', '安全',
               '光', '信息工程', '计算机病毒', '传感器', '操作系统', '应用软件', '科技', '软件测试', '计算机技术', '媒体', '广域网', '网络', '局域网', 'Linux',
               '信息技术', '信息', '一系列', '数据结构', '微电子', '算法', 'Java', '自动化', '入侵', '电子商务', '硬件', '信号', '计算机控制', '网络工程',
               '数字电路', '电脑', '并行', '单片机', '软件', '光电', '信息处理', '通信工程', 'TCP', '通讯', '计算机科学', '自然语言', '电子线路', '广播电视',
               '电气', '集成系统', '网络系统', 'IT', '软件工程', '电子信息', '信息科学', '智能科学', '科学技术', '光电子', '图像', '计算机网络', '接口技术', '信号处理',
               '密码学', '网络管理', '电气工程', '数据库', '信息安全', '功能化', '信息管理', '数据处理', '微电子学', '电子设备']
    start_url = 'http://dbpub.cnki.net/Grid2008/Dbpub/Brief.aspx?ID=SCPD'

    custom_settings = {
        # 'DOWNLOAD_DELAY': 1,
    }

    def start_requests(self):
        script = """function main(splash)
    splash:init_cookies(splash.args.cookies)

    assert(splash:go(splash.args.url))
    assert(splash:wait(0.5))

    local js = [[
        $("[name='advancedvalue1']").val("%s");
        $("[name='imageField']").click();
        ]]

    -- 提交表单
    assert(splash:runjs(string.format(js, splash.args.query)))

    local function wait_for(splash, condition)
        while not condition() do
            splash:wait(0.5)
        end
    end

    -- 等待页面加载完毕
    wait_for(splash, function()
        return splash:evaljs([[document.getElementsByClassName('s_table').length > 0]])
    end)

    return {
        url = splash:url(),
        cookies = splash:get_cookies(),
        html = splash:html(),
    }
end"""

        for query in self.queries:
            yield SplashRequest(self.start_url, endpoint='execute', args={
                'lua_source': script,
                'query': query,
                'session_id': 1
            }, dont_filter=True, callback=self.parse)

    def parse(self, response: SplashJsonResponse):
        for item in response.css(".s_table > tbody > tr > td:nth-child(2) > a"):
            detail_url = item.css('::attr(href)').extract_first()
            yield SplashRequest(response.urljoin(detail_url),
                                endpoint='execute',
                                cache_args=['lua_source'],
                                args={
                                    'lua_source': default_script,
                                    'session_id': 1
                                }, callback=self.parse_detail)

        has_more = response.xpath('//a[contains(text(), "下页")]/@href').extract_first()
        if has_more:
            yield SplashRequest(response.urljoin(has_more),
                                endpoint='execute',
                                cache_args=['lua_source'],
                                args={
                                    'lua_source': default_script,
                                    'session_id': 1
                                }, callback=self.parse)

    def parse_detail(self, response: SplashJsonResponse):
        item = PatentItem(
            url=response.url,
            html=response.text,
            title=extract_text_by_css(
                response, 'body > table:nth-child(2) > tbody > tr > td:nth-child(2)'
            ),
            # 申请人
            author=split_str_by_semicolon(extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(2)'
            )),
            # 摘要
            abstract=extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(11) > td:nth-child(2)'
            ),

            application_number=extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2)'
            ),
            # 公开号
            publication_number=extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2)'
            ),

            # 申请日
            application_date=str_to_datetime(extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(4)'
            )),
            # 公开日
            publication_date=str_to_datetime(extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(4)'
            )),
            # 地址
            address=extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(4)'
            ),

            # 发明人
            inventor=split_str_by_semicolon(extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(5) > td:nth-child(2)'
            )),
            # 专利代理机构
            agency=extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(8) > td:nth-child(2)'
            ),
            # 代理人
            agent=split_str_by_semicolon(extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(8) > td:nth-child(4)'
            )),

            # 国省代码
            national_code=extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(10) > td:nth-child(2)'
            ),
            # 主权项
            sovereignty_item=extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(12) > td:nth-child(2)'
            ),
            # 页数
            page_number=convert_str_to_integer(extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(13) > td:nth-child(2)'
            )),
            # 主分类号
            patent_main_class=extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(14) > td:nth-child(2)'
            ),
            # 专利分类号
            patent_class=split_str_by_semicolon(extract_text_by_css(
                response, '#box > tbody:nth-child(1) > tr:nth-child(15) > td:nth-child(2)'
            )),
        )

        file_href = response.xpath('//a[contains(text(), "推荐下载阅读CAJ格式全文")]/@href').extract_first()
        if file_href:
            file_href = response.urljoin(file_href)
            r = requests.get(file_href)
            if r.status_code == 200:
                item['attachment'] = {
                    'filename': None,
                    'stream': io.BytesIO(r.content)
                }
                if 'Content-Disposition' in r.headers:
                    item['attachment']['filename'] = r.headers['Content-Disposition'].split('; ')[1].split('=', 1)[1]

        yield item
