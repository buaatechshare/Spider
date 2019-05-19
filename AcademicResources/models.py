from mongoengine import *


class IErmBase:
    # 爬取时间
    created_at = DateTimeField()
    # 是否传输
    transfer = BooleanField(default=False)


class ErmResourceItem(Document, IErmBase):
    meta = {'allow_inheritance': True}

    # URL
    url = StringField()
    # HTML代码
    html = StringField()
    # 标题
    title = StringField()
    # 作者（专利为申请人）
    author = ListField()
    # 摘要
    abstract = StringField()


class ErmPatent(ErmResourceItem):
    # 申请号
    application_number = StringField()
    # 公开号
    publication_number = StringField()

    # 申请日
    application_date = DateTimeField()
    # 公开日
    publication_date = DateTimeField()
    # 地址
    address = StringField()

    # 发明人
    inventor = ListField()
    # 专利代理机构
    agency = StringField()
    # 代理人
    agent = ListField()

    # 国省代码
    national_code = StringField()
    # 主权项
    sovereignty_item = StringField()
    # 页数
    page_number = IntField()
    # 主分类号
    patent_main_class = StringField()
    # 专利分类号
    patent_class = ListField()

    # 附件
    attachment = FileField()


class ErmAchievement(ErmResourceItem):
    # 第一完成单位
    institution = StringField()
    # 关键词
    keywords = ListField()

    # 中图分类号
    chinese_library_classification = ListField()
    # 学科分类号
    subject_classification = ListField()

    # 成果类别
    category = StringField()
    # 成果水平
    level = StringField()

    # 研究起止时间
    duration = StringField()
    # 评价形式
    evaluation_form = StringField()
    # 成果入库时间
    storage_year = IntField()

    # 附件
    attachment = FileField()


class ErmArticle(ErmResourceItem):
    # 百度学术paperuri
    paper_uri = StringField()

    # 出版源
    publish = StringField()
    # 被引量
    citation_times = IntField()

    # 文章来源
    source = ListField()
    # 分类号（从知网爬取）
    classification = ListField()
    # 关键词（从知网爬取）
    keywords = ListField()

    # 年度引用
    annual_citation = ListField()  # （实际上是JSON，数据库用JSONB存）


class ErmAuthor(Document, IErmBase):
    # ScholarID
    scholar_id = StringField()
    # 姓名
    name = StringField()
    # 机构
    institute = StringField()

    # 被引频次
    citation_times = IntField()
    # 成果数
    article_numbers = IntField()
    # H指数
    h_index = IntField()
    # G指数
    g_index = IntField()

    # 领域
    field = ListField()

    # 历史成果数
    history_article_numbers = ListField()
    # 历史被引量
    history_citation_times = ListField()
