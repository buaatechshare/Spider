# -*- coding: utf-8 -*-
import re
from urllib.parse import urlparse, parse_qs

import scrapy
from scrapy_splash import SplashRequest, SplashJsonResponse

from AcademicResources.helpers import extract_text_by_css, convert_str_to_integer, split_str_by_semicolon
from AcademicResources.items import ArticleItem, AuthorItem

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


class ArticleSpider(scrapy.Spider):
    name = 'article'
    allowed_domains = ['xueshu.baidu.com', 'kns.cnki.net']

    # 深度学习 软件 大数据 计算机 编程 程序 电子 通信 多媒体 网络网页
    queries = ['IP', '计算机专业', '器件', '通信', '空间信息', '汇编', '程序设计', '微机', '办公自动化', '集成电路', '设备', '计算机软件', '技术', '多媒体', '安全',
               '光', '信息工程', '计算机病毒', '传感器', '操作系统', '应用软件', '科技', '软件测试', '计算机技术', '媒体', '广域网', '网络', '局域网', 'Linux',
               '信息技术', '信息', '一系列', '数据结构', '微电子', '算法', 'Java', '自动化', '入侵', '电子商务', '硬件', '信号', '计算机控制', '网络工程',
               '数字电路', '电脑', '并行', '单片机', '软件', '光电', '信息处理', '通信工程', 'TCP', '通讯', '计算机科学', '自然语言', '电子线路', '广播电视',
               '电气', '集成系统', '网络系统', 'IT', '软件工程', '电子信息', '信息科学', '智能科学', '科学技术', '光电子', '图像', '计算机网络', '接口技术', '信号处理',
               '密码学', '网络管理', '电气工程', '数据库', '信息安全', '功能化', '信息管理', '数据处理', '微电子学', '电子设备']
    start_url = 'https://xueshu.baidu.com/'

    custom_settings = {
        # 'DOWNLOAD_DELAY': 1,
    }

    def start_requests(self):
        script = """function main(splash)
    splash:init_cookies(splash.args.cookies)

    assert(splash:go(splash.args.url))
    assert(splash:wait(0.5))

    local values = {
        wd = splash.args.query
    }

    local form = splash:select('#form')
    assert(form:fill(values))
    assert(form:submit())
    assert(splash:wait(2))


    return {
        url = splash:url(),
        cookies = splash:get_cookies(),
        html = splash:html()
    }
end"""

        for query in self.queries[:1]:
            yield SplashRequest(self.start_url, endpoint='execute', args={
                'lua_source': script,
                'query': query,
                'session_id': 1
            }, dont_filter=True, callback=self.parse)

    def parse(self, response: SplashJsonResponse):
        for item in response.css("#bdxs_result_lists .t > a"):
            script = """function main(splash)
    splash:init_cookies(splash.args.cookies)
    assert(splash:go(splash.args.url))
    assert(splash:wait(0.5))
    local lineMapCitedData = splash:evaljs("window.lineMapCitedData || []")

    return {
        url = splash:url(),
        cookies = splash:get_cookies(),
        html = splash:html(),
        lineMapCitedData = lineMapCitedData
    }
end"""

            detail_url = item.css('::attr(href)').extract_first()
            yield SplashRequest(response.urljoin(detail_url),
                                endpoint='execute',
                                cache_args=['lua_source'],
                                args={
                                    'lua_source': script,
                                    'session_id': 1
                                }, callback=self.parse_detail)

        has_more = response.xpath('//*[@id="page"]//a[contains(text(), "下一页")]/@href').extract_first()
        if has_more:
            yield SplashRequest(response.urljoin(has_more),
                                endpoint='execute',
                                cache_args=['lua_source'],
                                args={
                                    'lua_source': default_script,
                                    'session_id': 1
                                }, callback=self.parse)

    def parse_detail(self, response: SplashJsonResponse):
        annual_citation = response.data['lineMapCitedData']
        for index, item in enumerate(annual_citation):
            annual_citation[index] = {'cited': int(item['cited']), 'total': int(item['total']),
                                      'year': int(item['year'])}

        item = ArticleItem(
            url=response.url,
            html=response.text,

            title=extract_text_by_css(response, '#dtl_l > div:nth-child(1) > h3:nth-child(1)'),
            author=extract_text_by_css(response, '.author_text > a', force_list=True),
            abstract=extract_text_by_css(response, '.abstract'),

            # 百度学术paperuri
            paper_uri=parse_qs(urlparse(response.url).query)['wd'][0][len('paperuri:('):-len(')')],

            # 出版源
            publish=extract_text_by_css(response, '.publish_text'),
            # 被引量
            citation_times=convert_str_to_integer(extract_text_by_css(response, '.sc_cite_cont')),

            # 文章来源
            source=[{
                'name': item.xpath('./*[@class="dl_source"]/text()').extract_first().strip(),
                'url': item.xpath('./@href').extract_first().strip(),
            } for item in
                response.xpath('//*[@id="allversion_wr"]//*[@class="dl_item_span"]/a[@target]')],
            # 分类号（从知网爬取）
            classification=[],
            # 关键词（从知网爬取）
            keywords=extract_text_by_css(response, '.dtl_search_word > div > a', recursive=False, force_list=True),

            # 年度引用
            annual_citation=annual_citation,
        )

        has_yield = False
        for source in item['source']:
            if source['name'] == '知网':
                cnki_net_url, = parse_qs(urlparse(source['url']).query)['sc_vurl']
                yield SplashRequest(cnki_net_url,
                                    endpoint='execute',
                                    cache_args=['lua_source'],
                                    meta={
                                        'item': item,
                                    },
                                    args={
                                        'lua_source': default_script,
                                        'session_id': 1
                                    }, callback=self.parse_extra_from_cnki_net)
                has_yield = True
                break

        if not has_yield:
            yield item

        for author in response.css('.author_text > a::attr(href)').extract():
            script = """function main(splash)
    splash:init_cookies(splash.args.cookies)
    assert(splash:go(splash.args.url))
    assert(splash:wait(0.5))
    local lineMapCitedData = splash:evaljs("window.lineMapCitedData || []")
    local lineMapAchData = splash:evaljs("window.lineMapAchData || []")

    return {
        url = splash:url(),
        cookies = splash:get_cookies(),
        html = splash:html(),
        lineMapCitedData = lineMapCitedData,
        lineMapAchData = lineMapAchData
    }
end"""

            author_url = response.urljoin(author.strip())
            yield SplashRequest(author_url,
                                endpoint='execute',
                                cache_args=['lua_source'],
                                args={
                                    'lua_source': script,
                                    'session_id': 1
                                }, callback=self.parse_author)

    def parse_extra_from_cnki_net(self, response: SplashJsonResponse):
        item = response.meta['item']

        classification = response.xpath('//label[@id="catalog_ZTCLS"]/../text()').extract_first()
        item['classification'] = classification.split(';') if classification else []
        item['keywords'] = extract_text_by_css(
            response, '.wxBaseinfo #catalog_KEYWORD ~ *'
        )
        yield item

    def parse_author(self, response: SplashJsonResponse):
        if not re.match(r'http(s)?://xueshu\.baidu\.com/scholarID/.+', response.url):
            return
        item = AuthorItem(
            scholar_id=extract_text_by_css(response, '.p_scholarID_id'),
            name=extract_text_by_css(response, '.person_baseinfo > .p_name'),
            institute=extract_text_by_css(response, '.person_baseinfo > .p_affiliate'),

            citation_times=convert_str_to_integer(
                extract_text_by_css(response, 'li.p_ach_item:nth-child(1) > p:nth-child(2)')),
            article_numbers=convert_str_to_integer(
                extract_text_by_css(response, 'li.p_ach_item:nth-child(2) > p:nth-child(2)')),
            h_index=convert_str_to_integer(
                extract_text_by_css(response, 'li.p_ach_item:nth-child(3) > p:nth-child(2)')),
            g_index=convert_str_to_integer(
                extract_text_by_css(response, 'li.p_ach_item:nth-child(4) > p:nth-child(2)')),

            field=split_str_by_semicolon(
                extract_text_by_css(response, '.person_editinfo .person_domain'),
                '/'),

            history_article_numbers=response.data['lineMapAchData'],
            history_citation_times=response.data['lineMapCitedData']
        )
        yield item
