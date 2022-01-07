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
    name = "kingpower"
    start_urls = 'https://www.kingpower.com/brands?lang=en'
    count = 1

    def start_requests(self):

        yield Request(self.start_urls , callback=self.parse)

    def parse(self, response):
        urls = response.xpath('//label[@class="s1qhqpzp-8 kqkGUX"]/a')
        for url_tag in urls:
            url = url_tag.xpath('./@href').extract_first()
            # url = 'https://www.kingpower.com/brand/calvin-klein?lang=en'
            brand = url_tag.xpath('./text()').extract_first()
            yield Request(response.urljoin(url)+'?lang=en', self.parseProducts, meta={'brand': brand, 'page':1})
            # break
    def parseProducts(self, response):
        urls = response.xpath('//a[@class="s1xmjep2-7 fCMcWq"]/@href').extract()
        for url in urls:
            yield Request(response.urljoin(url), self.parseFinal, meta={'brand': response.meta['brand']})

        next = response.xpath('//span[@aria-label="Next"]/parent::a[1]/parent::li[1]')
        if next and next != "disabled" :
            text = next.xpath('./@class').extract_first()
            if not text or text != "disabled":
                pagenum = int(response.meta['page']) + 1
                if not 'page=' in response.url:
                    url = response.url +'&page=2'
                else:
                    url = response.url.split('page=')[0] + 'page={}'.format(pagenum)
                yield Request(url, self.parseProducts, meta={'brand': response.meta['brand'], 'page': pagenum}, dont_filter=True)

    def parseFinal(self, response):
        item = OrderedDict()
        item['Serial'] = ''
        item['Platform URL'] = 'https://www.kingpower.com'
        item['Product Name'] = response.xpath('//title/text()').extract_first()
        prices= response.xpath('//span[@id="product-detail-label-product-price"]/span/text()').re(r'[\d.,]+')
        if prices:
            item['Product Price'] = prices[0].replace(',', '')
        else:
            item['Product Price'] = ''

        item['Product Price Currency'] = 'THB'
        item['Product Description'] = '\n'.join(response.xpath('//div[@id="product-detail-label-shortdescription"]/text()').extract()).strip()
        if item['Product Description'] == '' :
            try:
                desc = response.body.split('"longDescription":"')[-1].split('","dutyFree')[0].encode('utf-8').decode('unicode-escape')
                item['Product Description'] = desc
            except:
                item['Product Description'] = ''
        # categories = response.xpath('//p[@class="breadcrumbs"]/span/a/text()').extract()
        # if categories:
        #     categories = categories[:-1]
        #     item['Product Category'] = '/'.join(categories)
        # else:
        item['Product Category'] = '/'.join(response.xpath('//*[contains(@id, "breadcrumb-list-link")]/text()').extract())


        item['Image URL'] = response.xpath('//div[contains(@class, "slick-slide slick-active")]/img/@src').extract_first()
        if item['Image URL']:
            item['Image URI'] = item['Image URL'].split('/')[-1]
        item['Product URL'] = response.url
        item['Serial'] = self.count
        item['Brand'] = response.meta['brand']
        self.count += 1
        print self.count
        yield item
