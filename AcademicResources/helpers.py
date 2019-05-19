import datetime
import re

import iso8601
import pytz

# user-gent
iPhone_Safari = 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) ' \
                'Version/10.0 Mobile/14E304 Safari/602.1'

Windows_Edge = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 ' \
               'Safari/537.36 Edge/15.15063'

Linux_Firefox = 'Mozilla/5.0 (X11; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0'

Baidu_Spider = 'Mozilla/5.0 (Linux;u;Android 4.2.2;zh-cn;) AppleWebKit/534.46 (KHTML,like Gecko) Version/5.1 Mobile ' \
               'Safari/10600.6.3 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'


def convert_str_to_integer(value) -> (int, None):
    if type(value) is list and len(value) > 0:
        value = value[0]
    if type(value) is int:
        return value
    elif type(value) is str:
        match_result = re.match('(\d+)[.]?(\d+)?([w万亿])?', value.strip())
        if match_result is not None:
            match_result = match_result.groups()
            integer = match_result[0]
            if match_result[1] is not None:
                decimal = match_result[1]
            else:
                decimal = '0'
            if match_result[2] == '万' or match_result[2] == 'w':
                exponential = 1e4
            elif match_result[2] == '亿':
                exponential = 1e8
            else:
                exponential = 1.0
            return int(float("%s.%s" % (integer, decimal)) * exponential)
    return None


def str_to_datetime(value: (str, None)) -> datetime:
    try:
        return iso8601.parse_date(value, default_timezone=pytz.timezone('Asia/Shanghai'))
    except iso8601.ParseError:
        return None


def human_str_to_datetime(value: (str, None)) -> datetime:
    def match_time(raw_str: str) -> datetime:
        now = datetime.datetime.now()

        matches = re.match(r'^(\d+)\s*分钟前', raw_str)
        if matches:
            groups = matches.groups()
            return now - datetime.timedelta(minutes=int(groups[0]))

        matches = re.match(r'^今天\s*(\d+):(\d+):?(\d+)?', raw_str)
        if matches:
            groups = matches.groups()
            return datetime.datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=int(groups[0]),
                minute=int(groups[1]),
                second=int(groups[2]) if groups[2] else 0
            )

        matches = re.match(r'^昨天\s*(\d+):(\d+):?(\d+)?', raw_str)
        if matches:
            groups = matches.groups()
            return datetime.datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=int(groups[0]),
                minute=int(groups[1]),
                second=int(groups[2]) if groups[2] else 0
            ) - datetime.timedelta(days=1)

        matches = re.match(r'^(\d+)[月-](\d+)[日\s]?\s*(\d+):(\d+):?(\d+)?', raw_str)
        if matches:
            groups = matches.groups()
            return datetime.datetime(
                year=now.year,
                month=int(groups[0]),
                day=int(groups[1]),
                hour=int(groups[2]),
                minute=int(groups[3]),
                second=int(groups[4]) if groups[4] else 0
            )

        matches = re.match(r'^(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):?(\d+)?', raw_str)
        if matches:
            groups = matches.groups()
            return datetime.datetime(
                year=int(groups[0]) if len(groups[0]) == 4 else int("20" + groups[0]),
                month=int(groups[1]),
                day=int(groups[2]),
                hour=int(groups[3]),
                minute=int(groups[4]),
                second=int(groups[5]) if groups[5] else 0
            )
        return None

    return match_time(value) if value else None


def extract_text_by_css(_response, query, recursive=True, force_list=False):
    selector = _response.css(query)

    text_list = []
    for item in selector:
        if recursive:
            parts = item.xpath('.//text()').extract()
        else:
            parts = item.xpath('./text()').extract()
        if len(parts) > 0:
            parts = ''.join([part.strip() for part in parts])
            text_list.append(re.sub(r'[\xa0\u200b\u3000]', ' ', parts).strip(';；'))
    if len(text_list) == 0:
        return None
    if len(text_list) == 1 and not force_list:
        return text_list[0]
    return text_list


def split_str_by_semicolon(_str, delimeter=';'):
    if not _str:
        return []
    return [i.strip() for i in _str.split(delimeter)]
