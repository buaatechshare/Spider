#!/usr/bin/env python3
import datetime
import hmac
import json
import random
import string
import sys
from urllib.parse import urljoin, quote

import mongoengine
import requests
from mongoengine import GridFSProxy

from AcademicResources.models import ErmPatent, ErmAchievement, ErmArticle, ErmAuthor

base_url = 'http://47.94.96.70:9902/'

patent_url = urljoin(base_url, 'api/spider/patent')
achievement_url = urljoin(base_url, 'api/spider/project')
article_url = urljoin(base_url, 'api/spider/paper')

author_url = urljoin(base_url, 'api/spider/expert')

web_io_url = 'http://47.94.96.70:8080/ERM-WebIO-1.0/file/upload.do'

key = 'gGwk3g8JwUJ7qAWKWNd9dGEX4HjNnshr'


def generate_hash(url, timestamp, nonce, text):
    data = (url + timestamp + nonce + text)
    h = hmac.new(key.encode(), data.encode(), digestmod='SHA256')
    signature = h.hexdigest()
    return {
        'timestamp': timestamp,
        'nonce': nonce,
        'signature': signature
    }


def request_post_encrypted(url, json_data):
    timestamp = str(int(datetime.datetime.now().timestamp()))
    nonce = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(8)])
    text = json.dumps(json_data)
    params = generate_hash(url, timestamp, nonce, text)
    return requests.post(url=url, params=params, data=text)


def sync_erm_patent():
    # ErmPatent
    for index, patent_item in enumerate(ErmPatent.objects(transfer__ne=True)):
        attachment = patent_item['attachment']
        assert isinstance(attachment, GridFSProxy)

        if attachment.grid_id and attachment.get().filename:
            filename = attachment.get().filename

            r = requests.post(web_io_url, files={
                'file': (quote(filename), attachment)
            })

            attachment = json.loads(r.text)['link']
        else:
            attachment = None

        post_item = {
            'url': patent_item['url'],
            'html': patent_item['html'],
            'title': patent_item['title'],
            'introduction': patent_item['abstract'],
            'author': patent_item['author'],

            'application_number': patent_item['application_number'],
            'publication_number': patent_item['publication_number'],
            'application_date': patent_item['application_date'].isoformat() + 'Z',
            'publication_date': patent_item['publication_date'].isoformat() + 'Z',
            'address': patent_item['address'],
            'inventor': patent_item['inventor'],
            'agency': patent_item['agency'],
            'agent': patent_item['agent'],
            'national_code': patent_item['national_code'],
            'sovereignty_item': patent_item['sovereignty_item'],
            'page_number': patent_item['page_number'],
            'patent_main_class': patent_item['patent_main_class'],
            'patent_class': patent_item['patent_class'],
            'attachment': attachment
        }
        r = request_post_encrypted(patent_url, json_data=post_item)

        try:
            status = json.loads(r.text)['status']
            if status != 'succ':
                raise Exception()
        except:
            print(r.text)
            exit(1)

        patent_item['transfer'] = True
        patent_item.save()
        print("ErmPatent %d finished.\t%s" % (index + 1, r.text))


def sync_erm_achievement():
    # ErmAchievement
    for index, achievement_item in enumerate(ErmAchievement.objects(transfer__ne=True)):
        attachment = achievement_item['attachment']
        assert isinstance(attachment, GridFSProxy)

        if attachment.grid_id and attachment.get().filename:
            filename = attachment.get().filename
            r = requests.post(web_io_url, files={
                'file': (quote(filename), attachment)
            })

            attachment = json.loads(r.text)['link']
        else:
            attachment = None

        post_item = {
            'url': achievement_item['url'],
            'html': achievement_item['html'],
            'title': achievement_item['title'],
            'introduction': achievement_item['abstract'],
            'author': achievement_item['author'] or [achievement_item['institution']],

            'institution': achievement_item['institution'],
            'keywords': achievement_item['keywords'],
            'chinese_library_classification': achievement_item['chinese_library_classification'],
            'subject_classification': achievement_item['subject_classification'],
            'category': achievement_item['category'],
            'level': achievement_item['level'],
            'duration': achievement_item['duration'],
            'evaluation_form': achievement_item['evaluation_form'],
            'storage_year': achievement_item['storage_year'],

            'attachment': attachment,
        }
        r = request_post_encrypted(achievement_url, json_data=post_item)

        try:
            status = json.loads(r.text)['status']
            if status != 'succ':
                raise Exception()
        except:
            print(r.text)
            continue

        achievement_item['transfer'] = True
        achievement_item.save()

        print("ErmAchievement %d finished.\t%s" % (index + 1, r.text))


def sync_erm_article():
    with open('clc.json') as fp:
        clc = json.loads(fp.read())

    # ErmArticle
    for index, article_item in enumerate(ErmArticle.objects(transfer__ne=True, author__ne=[])):
        post_item = {
            'url': article_item['url'],
            'html': article_item['html'],
            'title': article_item['title'],
            'introduction': article_item['abstract'],
            'author': article_item['author'],

            'publish': article_item['publish'],
            'citation_times': article_item['citation_times'],
            'source': article_item['source'],

            'classification': article_item['classification'],
            'field': [clc[item] for item in article_item['classification'] if item in clc],

            'keywords': article_item['keywords'],
            'annual_citation': article_item['annual_citation']
        }

        r = request_post_encrypted(article_url, json_data=post_item)

        try:
            status = json.loads(r.text)['status']
            if status != 'succ':
                raise Exception()
        except:
            print(r.text)
            continue

        article_item['transfer'] = True
        article_item.save()

        print("ErmArticle %d finished.\t%s" % (index + 1, r.text))


def sync_erm_author():
    # ErmAuthor
    for index, author_item in enumerate(ErmAuthor.objects(transfer__ne=True)):
        post_item = {
            'ScholarID': author_item['scholar_id'],
            'name': author_item['name'],
            'institute': author_item['institute'],
            'citation_times': author_item['citation_times'],
            'article_numbers': author_item['article_numbers'],
            'h_index': author_item['h_index'],
            'g_index': author_item['g_index'],
            'field': author_item['field'],

            'history_article_numbers': author_item['history_article_numbers'],
            'history_citation_times': author_item['history_citation_times']
        }

        r = request_post_encrypted(author_url, json_data=post_item)

        try:
            status = json.loads(r.text)['status']
            if status != 'succ':
                raise Exception()
        except:
            print(r.text)
            continue

        author_item['transfer'] = True
        author_item.save()

        print("ErmAuthor %d finished.\t%s" % (index + 1, r.text))


if __name__ == "__main__":
    mongoengine.connect('erm')

    mapper = {
        'patent': sync_erm_patent,
        'achievement': sync_erm_achievement,
        'article': sync_erm_article,
        'author': sync_erm_author,
    }
    if len(sys.argv) == 1:
        for key, callback in mapper.items():
            callback()
    else:
        for cmd in sys.argv[1:]:
            if cmd in mapper:
                mapper[cmd]()
            else:
                print('%s can not recognize.' % cmd)
