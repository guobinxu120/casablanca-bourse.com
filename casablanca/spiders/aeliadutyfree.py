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
    name = "aeliadutyfree"
    start_urls = 'https://www.aeliadutyfree.fr/nice/en/'
    count = 1

    def start_requests(self):
        yield Request(self.start_urls , callback=self.parse)

    def parse(self, response):
        parent_tags = response.xpath('//li[contains(@class, "level1 nav")]')
        for parent_tag in parent_tags:
            child_urls = parent_tag.xpath('.//li[contains(@class, "level2")]/a/@href').extract()
            if parent_tag:
                for url in child_urls:
                    yield Request(url, self.parseProducts, meta={'page':1})
            else:
                url = parent_tag.xpath('./a/@href').extract_first()
                yield Request(url, self.parseProducts, meta={'page':1})


    def parseProducts(self, response):
        urls = response.xpath('//li[@class="item last"]//a[@class="product-link"]/@href').extract()
        for url in urls:
            yield Request(response.urljoin(url), self.parseFinal)

        total = response.xpath('//div[@class="product-number"]/strong/span/text()').extract_first()
        pagenum = response.meta['page']
        if int(total) > (pagenum * 24):
            pagenum = int(response.meta['page']) + 1
            if not 'p=' in response.url:
                url = response.url +'?p=2'
            else:
                url = response.url.split('p=')[0] + 'p={}'.format(pagenum)
            yield Request(url, self.parseProducts, meta={ 'page': pagenum})

    def parseFinal(self, response):
        item = OrderedDict()
        item['Serial'] = ''
        item['Platform URL'] = 'https://www.aeliadutyfree.fr'
        item['Product Name'] = response.xpath('//span[@class="product-name"]/text()').extract_first()
        item['Brand'] = response.xpath('//span[@class="manufacturer"]/text()').extract_first()
        prices= response.xpath('//div[@class="price-info"]//span[@class="price"]/text()').re(r'[\d.,]+')
        if prices:
            item['Product Price'] = prices[0]
        else:
            item['Product Price'] = ''

        item['Product Price Currency'] = 'EUR'
        item['Product Description'] = '\n'.join(response.xpath('//div[@class="std"]/text()').extract()).strip()
        # if item['Product Description'] == '' :
        #     try:
        #         desc = response.body.split('"longDescription":"')[-1].split('","dutyFree')[0].encode('utf-8').decode('unicode-escape')
        #         if 'span' in desc:
        #             resp = TextResponse(url='',body=desc,encoding='utf-8')
        #             desc = '\n'.join(resp.xpath('//span//text()').extract()).strip()
        #         elif '<li>' in desc:
        #             resp = TextResponse(url='',body=desc,encoding='utf-8')
        #             desc = '\n'.join(resp.xpath('//li//text()').extract()).strip()
        #         item['Product Description'] = desc
        #     except:
        #         item['Product Description'] = ''
        # categories = response.xpath('//p[@class="breadcrumbs"]/span/a/text()').extract()
        # if categories:
        #     categories = categories[:-1]
        #     item['Product Category'] = '/'.join(categories)
        # else:

        item['Product Category'] = '/'.join(response.xpath('//div[@class="breadcrumbs"]//li[contains(@class, "category")]/a/text()').extract())


        item['Image URL'] = response.xpath('//div[@class="product-image-gallery"]/img/@src').extract_first()
        if item['Image URL']:
            item['Image URI'] = item['Image URL'].split('/')[-1]
        item['Product URL'] = response.url
        item['Serial'] = self.count
        self.count += 1
        yield item
