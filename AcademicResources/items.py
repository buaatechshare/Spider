# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html


import scrapy


class IBaseItem(scrapy.Item):
    # 爬取时间
    created_at = scrapy.Field()


class ResourceItem(IBaseItem):
    url = scrapy.Field()
    html = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    abstract = scrapy.Field()


class PatentItem(ResourceItem):
    # 申请号
    application_number = scrapy.Field()
    # 公开号
    publication_number = scrapy.Field()

    # 申请日
    application_date = scrapy.Field()
    # 公开日
    publication_date = scrapy.Field()
    # 地址
    address = scrapy.Field()

    # 发明人
    inventor = scrapy.Field()
    # 专利代理机构
    agency = scrapy.Field()
    # 代理人
    agent = scrapy.Field()

    # 国省代码
    national_code = scrapy.Field()
    # 主权项
    sovereignty_item = scrapy.Field()
    # 页数
    page_number = scrapy.Field()
    # 主分类号
    patent_main_class = scrapy.Field()
    # 专利分类号
    patent_class = scrapy.Field()

    # 附件
    attachment = scrapy.Field()


class AchievementItem(ResourceItem):
    # 第一完成单位
    institution = scrapy.Field()
    # 关键词
    keywords = scrapy.Field()

    # 中图分类号
    chinese_library_classification = scrapy.Field()
    # 学科分类号
    subject_classification = scrapy.Field()

    # 成果类别
    category = scrapy.Field()
    # 成果水平
    level = scrapy.Field()

    # 研究起止时间
    duration = scrapy.Field()
    # 评价形式
    evaluation_form = scrapy.Field()
    # 成果入库时间
    storage_year = scrapy.Field()

    # 附件
    attachment = scrapy.Field()


class ArticleItem(ResourceItem):
    # 百度学术paperuri
    paper_uri = scrapy.Field()

    # 出版源
    publish = scrapy.Field()
    # 被引量
    citation_times = scrapy.Field()

    # 文章来源
    source = scrapy.Field()
    # 分类号（从知网爬取）
    classification = scrapy.Field()
    # 关键词（从知网爬取）
    keywords = scrapy.Field()

    # 年度引用
    annual_citation = scrapy.Field()


class AuthorItem(IBaseItem):
    # ScholarID
    scholar_id = scrapy.Field()
    # 姓名
    name = scrapy.Field()
    # 机构
    institute = scrapy.Field()

    # 被引频次
    citation_times = scrapy.Field()
    # 成果数
    article_numbers = scrapy.Field()
    # H指数
    h_index = scrapy.Field()
    # G指数
    g_index = scrapy.Field()

    # 领域
    field = scrapy.Field()

    # 历史成果数
    history_article_numbers = scrapy.Field()
    # 历史被引量
    history_citation_times = scrapy.Field()
