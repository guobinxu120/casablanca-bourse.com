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
    name = "everrich"
    start_urls = 'https://www.everrich.com/tw/'
    count = 1

    def start_requests(self):

        yield Request(self.start_urls , callback=self.parse)

    def parse(self, response):
        urls = response.xpath('//div[@class="sub-menu--category"]//li/a')
        for url_tag in urls:
            url = url_tag.xpath('./@href').extract_first()
            category = url_tag.xpath('./text()').extract_first()
            yield Request(url, self.parseProducts, meta={'category': category, 'page':1})

    def parseProducts(self, response):
        items = response.xpath('//div[@class="category-items"]/div/ul/li')
        for li in items:
            item = OrderedDict()
            item['Serial'] = self.count
            item['Platform URL'] = 'https://www.everrich.com'
            item['Product Name'] = li.xpath('./@data-item-english-name').extract_first()
            prices= li.xpath('./@data-item-price').re(r'[\d.,]+')
            if prices:
                item['Product Price'] = prices[0]
            else:
                item['Product Price'] = ''

            item['Product Price Currency'] = 'TWD'
            item['Product Description'] = '\n'.join(li.xpath('.//div[@class="product-more-info__headings"]/a/p/text()').extract()).strip()
            cates = response.xpath('//div[@class="big-bread"]//span[@itemprop="name"]/text()').extract()
            category = []
            for cat in cates:
                category.append(cat.strip())

            item['Product Category'] = '/'.join(category)

            item['Image URL'] = li.xpath('./@data-item-image').extract_first()
            if item['Image URL']:
                item['Image URI'] = item['Image URL'].split('/')[-1]
            item['Product URL'] = li.xpath('./@data-item-link').extract_first()
            self.count += 1
            print self.count
            yield item

        # next = response.xpath('//button[@class="page-next pagination-button"]/@data-target-page').extract_first()
        # if next:
        next = int(response.meta['page']) + 1
        final = response.xpath('//ul[@class="pagination-list"]/li/button/@data-target-page').extract()
        if next < int(final[-1]):
            if 'page=' in response.url:
                url = response.url.replace('page={}'.format(response.meta['page']), 'page={}'.format(next))
            else:
                if '?' in response.url:
                    url = response.url + '&page={}'.format(next)
                else:
                    url = response.url + '?page={}#page={}'.format(next, next)
            yield Request(url, self.parseProducts, meta={'category': response.meta['category'], 'page': next})

    # def parseFinal(self, response):
    #     item = OrderedDict()
    #     item['Serial'] = ''
    #     item['Platform URL'] = 'http://www.heinemann-dutyfree.com'
    #     item['Product Name'] = response.xpath('//h1[@id="title-ellipsis"]/text()').extract_first()
    #     prices= response.xpath('//span[@id="price"]/text()').re(r'[\d.,]+')
    #     if prices:
    #         item['Product Price'] = prices[0]
    #     else:
    #         item['Product Price'] = ''
    #
    #     item['Product Price Currency'] = 'EUR'
    #     item['Product Description'] = '\n'.join(response.xpath('//div[@class="accordion"]/section/div[@class="content"]//text()').extract()).strip()
    #     # categories = response.xpath('//p[@class="breadcrumbs"]/span/a/text()').extract()
    #     # if categories:
    #     #     categories = categories[:-1]
    #     #     item['Product Category'] = '/'.join(categories)
    #     # else:
    #     item['Product Category'] = response.meta['category']
    #
    #
    #     item['Image URL'] = response.xpath('//img[@id="flyout1"]/@src').extract_first()
    #     if item['Image URL']:
    #         item['Image URI'] = item['Image URL'].split('/')[-1]
    #     item['Product URL'] = response.url
    #     item['Serial'] = self.count
    #     self.count += 1
    #     yield item


