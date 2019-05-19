# -*- coding: utf-8 -*-
import io

import requests
import scrapy
from scrapy_splash import SplashRequest, SplashJsonResponse

from AcademicResources.helpers import extract_text_by_css
from AcademicResources.items import ArticleItem

default_script = """function main(splash)
    splash:init_cookies(splash.args.cookies)
    assert(splash:go(splash.args.url, nil, splash.args.headers))
    assert(splash:wait(0.5))

    return {
        url = splash:url(),
        cookies = splash:get_cookies(),
        html = splash:html()
    }
end"""


class ArticleSpider(scrapy.Spider):
    name = 'article_bak'
    allowed_domains = ['cnki.net']
    queries = ['深度学习', '软件', '大数据', '计算机', '编程', '程序', '电子', '通信', '多媒体', '网络网页']
    start_url = 'http://kns.cnki.net/kns/index.html?code=CJFQ'

    custom_settings = {
        # 'DOWNLOAD_DELAY': 1,
    }

    def start_requests(self):
        script = """function main(splash)
    splash:init_cookies(splash.args.cookies)

    assert(splash:go(splash.args.url))
    assert(splash:wait(0.5))

    local js = [[
        $("#txt_SearchText").val("%s");
        directUrl();
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
        return splash:evaljs([[
            ((document.getElementById('iframeResult') || {}).src || '')
                .indexOf('http://kns.cnki.net/kns/brief/brief.aspx') !== -1
         ]])
    end)
    
    local frame_src = splash:evaljs([[ (document.getElementById('iframeResult')||{}).src ]])
    assert(splash:go(frame_src))
    assert(splash:wait(0.5))

    return {
        url = splash:url(),
        cookies = splash:get_cookies(),
        html = splash:html()
    }
end"""

        for query in self.queries:
            yield SplashRequest(self.start_url, endpoint='execute', args={
                'lua_source': script,
                'query': query,
                'session_id': 1
            }, dont_filter=True, callback=self.parse)

    def parse(self, response: SplashJsonResponse):
        for item in response.css(".GridTableContent > tbody > tr > td:nth-child(2) > a"):
            detail_url = item.css('::attr(href)').extract_first()
            yield SplashRequest(response.urljoin(detail_url),
                                endpoint='execute',
                                cache_args=['lua_source'],
                                headers={
                                    'Referer': response.url
                                },
                                args={
                                    'lua_source': default_script,
                                    'session_id': 1
                                }, callback=self.parse_detail)

        has_more = response.xpath('//a[contains(text(), "下一页")]/@href').extract_first()
        if has_more:
            yield SplashRequest(response.urljoin(has_more),
                                endpoint='execute',
                                cache_args=['lua_source'],
                                args={
                                    'lua_source': default_script,
                                    'session_id': 1
                                }, callback=self.parse)

    def parse_detail(self, response: SplashJsonResponse):
        item = ArticleItem(
            url=response.url,
            html=response.text,
            title=extract_text_by_css(
                response, '.wxTitle .title'
            ),

            # 作者
            author=extract_text_by_css(
                response, '.wxTitle > .author > span'
            ),
            # 单位
            institution=extract_text_by_css(
                response, '.wxTitle > .orgn > span'
            ),

            # 摘要
            abstract=extract_text_by_css(
                response, '.wxBaseinfo #ChDivSummary'
            ),
            # 基金
            fund=extract_text_by_css(
                response, '.wxBaseinfo #catalog_FUND ~ *'
            ),
            # 关键词
            keywords=extract_text_by_css(
                response, '.wxBaseinfo #catalog_KEYWORD ~ *'
            ),

            # 中图分类号
            classification=response.xpath('//label[@id="catalog_ZTCLS"]/../text()').extract_first()
        )

        file_href = response.css('#pdfDownF::attr(href)').extract_first() or response.css(
            '#cajDownF::attr(href)').extract_first()
        if file_href:
            file_href = response.urljoin(file_href)

            cookies = requests.utils.dict_from_cookiejar(response.cookiejar)
            headers = {'Referer': response.url}
            r = requests.get(file_href, cookies=cookies, headers=headers)

            if r.status_code == 200:
                item['attachment'] = {
                    'filename': None,
                    'stream': io.BytesIO(r.content)
                }
                if 'Content-Disposition' in r.headers:
                    filename = r.headers['Content-Disposition'].split('; ')[1].split('=', 1)[1]
                    item['attachment']['filename'] = filename.encode('ISO-8859-1').decode('gbk')

        yield item
