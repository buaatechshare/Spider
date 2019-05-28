# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
import time
import os
class PatentspiderPipeline(object):
    def __init__(self):
        now = time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time())) 
        store_file=os.path.dirname(__file__)+'/spiders/'+now+' patent_result.json'
        # self.file=codecs.open('result_patent.json','w',encoding='utf-8')
        self.file=codecs.open(store_file,'w',encoding='utf-8')
    def process_item(self, item, spider):
        # json 格式储存
        lines=json.dumps(dict(item),ensure_ascii=False)+"\n"
        self.file.write(lines)
        return item

    def close_spider(self,spider):
        self.file.close()

