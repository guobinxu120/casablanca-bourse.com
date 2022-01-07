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
    name = "heinemann"
    start_urls = 'http://www.heinemann-dutyfree.com/frankfurt_en'
    count = 1

    def start_requests(self):

        yield Request(self.start_urls , callback=self.parse)

    def parse(self, response):
        urls = response.xpath('//a[@class="nav__items__link"]')
        for url_tag in urls:
            url = url_tag.xpath('./@href').extract_first()
            category = url_tag.xpath('./text()').extract_first()
            yield Request(url, self.parseProducts, meta={'category': category})

    def parseProducts(self, response):
        urls = response.xpath('//a[@class="product-slim-content"]/@href').extract()
        for url in urls:
            yield Request(url, self.parseFinal, meta={'category': response.meta['category']})

        next = response.xpath('//li[@class="next"]/a/@href').extract_first()
        if next:
            yield Request(response.urljoin(next), self.parseProducts, meta={'category': response.meta['category']})

    def parseFinal(self, response):
        item = OrderedDict()
        item['Serial'] = ''
        item['Platform URL'] = 'http://www.heinemann-dutyfree.com'
        item['Product Name'] = response.xpath('//h1[@id="title-ellipsis"]/text()').extract_first()
        prices= response.xpath('//span[@id="price"]/text()').re(r'[\d.,]+')
        if prices:
            item['Product Price'] = prices[0]
        else:
            item['Product Price'] = ''

        item['Product Price Currency'] = 'EUR'
        item['Product Description'] = '\n'.join(response.xpath('//div[@class="accordion"]/section/div[@class="content"]//text()').extract()).strip()
        # categories = response.xpath('//p[@class="breadcrumbs"]/span/a/text()').extract()
        # if categories:
        #     categories = categories[:-1]
        #     item['Product Category'] = '/'.join(categories)
        # else:
        item['Product Category'] = response.meta['category']


        item['Image URL'] = response.xpath('//img[@id="flyout1"]/@src').extract_first()
        if item['Image URL']:
            item['Image URI'] = item['Image URL'].split('/')[-1]
        item['Product URL'] = response.url
        item['Serial'] = self.count
        self.count += 1
        yield item


