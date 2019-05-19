# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime

import mongoengine
import scrapy

from AcademicResources.items import ResourceItem, PatentItem, AchievementItem, ArticleItem, AuthorItem
from AcademicResources.models import ErmResourceItem, ErmPatent, ErmAchievement, ErmArticle, ErmAuthor


class AcademicresourcesPipeline(object):

    def open_spider(self, spider):
        mongoengine.connect('erm')

    def close_spider(self, spider):
        pass

    def process_item(self, item: scrapy.Item, spider):
        item['created_at'] = datetime.datetime.now()

        if isinstance(item, ResourceItem):
            if len(ErmResourceItem.objects(title=item['title'])) > 0:
                return item

            if isinstance(item, PatentItem):
                tmp_item = dict(item)
                if 'attachment' in tmp_item:
                    attachment = tmp_item.pop('attachment')
                else:
                    attachment = None
                ErmItem = ErmPatent(**tmp_item)
                if attachment:
                    ErmItem.attachment.put(attachment['stream'], filename=attachment['filename'])
                ErmItem.save()

            elif isinstance(item, AchievementItem):
                tmp_item = dict(item)
                if 'attachment' in tmp_item:
                    attachment = tmp_item.pop('attachment')
                else:
                    attachment = None
                ErmItem = ErmAchievement(**tmp_item)
                if attachment:
                    ErmItem.attachment.put(attachment['stream'], filename=attachment['filename'])
                ErmItem.save()

            elif isinstance(item, ArticleItem):
                ErmItem = ErmArticle(**item)
                ErmItem.save()
        elif isinstance(item, AuthorItem):
            if len(ErmAuthor.objects(name=item['name'])) > 0:
                return item
            ErmItem = ErmAuthor(**item)
            ErmItem.save()

        return item
