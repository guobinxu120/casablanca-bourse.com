# -*- coding: utf-8 -*-
from scrapy import Spider, Request

import sys
import re, os, urllib
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time

from shutil import copyfile
import json, re, csv
from scrapy.http import FormRequest
from scrapy.http import TextResponse



class CasablancaSpider(Spider):
    name = "jrdutyfree"
    start_urls = 'https://www.jrdutyfree.com.au'
    count = 1
    use_selenium = False
    def start_requests(self):
        f1 = open('jrdutyfree_urls.csv')
        csv_items = csv.DictReader(f1)
        self.urls = []
        for i, row in enumerate(csv_items):
            self.urls.append(row)
        for category in self.urls:
            cat = category['cat']
            url = category['url']
            yield Request(url , callback=self.parse, meta={'category': cat})

    def parse(self, response):
        item = OrderedDict()
        item['Serial'] = ''
        item['Platform URL'] = 'https://www.jrdutyfree.com.au'
        item['Product Name'] = response.xpath('//span[@class="gallery-title-sub-heading"]/text()').extract_first()
        item['Brand'] = response.xpath('//div[@class="gallery-title"]//val/text()').extract_first()
        prices= response.xpath('//p[@class="product-cost"]/strong/text()').re(r'[\d.,]+')
        if prices:
            item['Product Price'] = prices[0]
        else:
            item['Product Price'] = ''

        item['Product Price Currency'] = 'AUD'
        item['Product Description'] = '\n'.join(response.xpath('//div[@class="wrap"]/p[2]//text()').extract())

        item['Product Category'] = response.meta['category']


        item['Image URL'] = response.xpath('//a[@class="popup-image"]/img/@src').extract_first()
        if item['Image URL']:
            item['Image URI'] = item['Image URL'].split('/')[-1]
        item['Product URL'] = response.url
        item['Serial'] = self.count
        self.count += 1
        yield item




