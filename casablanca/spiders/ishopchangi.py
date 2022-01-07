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
    name = "ishopchangi"
    start_urls = 'https://www.ishopchangi.com/'
    count = 1

    def start_requests(self):

        yield Request(self.start_urls , callback=self.parse)


    def parse(self, response):
        li_menu = response.xpath('//ul[@class="naver"]/li')
        for i, li in enumerate(li_menu):
            if i == 0: continue
            urls = li.xpath('.//div[@class="paged-columns"]//ul/a/li/parent::a/@href').extract()
            payload = {
                "categories":"783",
                "brand":"",
                "minPrice":0,
                "maxPrice":5000,
                "flightType":"departure|arrival|delivery|",
                "filterBy":"",
                "filterPageSize":"30",
                "currentPageindex":1,
                "langType":"en-US",
                "sortBy":"popularity",
                "tagName":"",
                "deliveryAvailable":""
            }
            for pro_url in urls:
                id = pro_url.split('-')[-1]
                payload['categories'] = id
                url = 'https://www.ishopchangi.com/WSHub/wsProduct.asmx/GetProductGroupByFilterEx'
                headers = {
                    "content-type": "application/json"
                }
                yield Request(url, self.parseProducts, method="POST", body=json.dumps(payload), headers=headers, meta={'payload': payload, 'url': pro_url}, dont_filter=True)

    def parseProducts(self, response):
        data = response.body.replace('\\', '').replace('{"d":"', '').replace(']}"}', ']}')
        count = int(data.replace('{"Count":', '').split(',')[0])
        try:
            p = re.compile(r'(?<=[a-zA-Z0-9\s])"(?=[a-zA-Z\s0-9])')
            data = p.sub("", data)

            json_data = json.loads(data)
            count = int(json_data['Count'])
            for item_data in json_data['Items']:
                item = OrderedDict()
                item['Serial'] = ''
                item['Platform URL'] = 'https://www.ishopchangi.com/'
                item['Product Name'] = item_data['ProductGroupTitle']
                item['Product Price'] = item_data['Disc_Price']
                item['Product Price Currency'] = 'SGD'
                item['Product Description'] = ''
                item['Product Category'] = item_data['CategoryDisplayName']
                item['Image URL'] = item_data['GroupImage']
                if item['Image URL']:
                    item['Image URI'] = item['Image URL'].split('/')[-1]
                item['Product URL'] = 'https://www.ishopchangi.com/product/' + str(item_data['ProductGroupTitleSlug']) + '-' + str(item_data['ProductGroupAutoID']) +'-' + str(item_data['LP_ConcessionaireAutoID'])
            # urls = response.xpath('//div[@class="productlist"]/div/div/@data-producturl').extract()
            # for url in urls:
                yield Request(item['Product URL'], self.parseFinal, meta={'item': item})
        except:
            pass
        # if len (json_data['Items']) < 1:
        #     pass


        payload = response.meta['payload']
        page = int(payload['currentPageindex'])
        if count > page * 30 :
            page += 1
            url = 'https://www.ishopchangi.com/WSHub/wsProduct.asmx/GetProductGroupByFilterEx'
            headers = {
                "content-type": "application/json"
            }
            payload['currentPageindex'] = str(page)
            yield Request(url, self.parseProducts, method="POST", body=json.dumps(payload), headers=headers, meta={'payload': payload, 'url': response.meta['url']}, dont_filter=True)

        # next = response.xpath('//ul[@class="productpagination"]/li/a[text()=">"]/@href').extract_first()
        # if next:
        #     yield Request(response.urljoin(next), self.parseProducts)

    def parseFinal(self, response):
        item = response.meta['item']
        item['Product Description'] = response.xpath('//meta[@property="og:description"]/@content').extract_first()
        item['Serial'] = self.count
        self.count += 1
        print(self.count)
        yield item

        # item['Serial'] = ''
        # item['Platform URL'] = 'https://www.ishopchangi.com/'
        # item['Product Name'] = response.xpath('//h1[@class="productname ng-binding"]/text()').extract_first()
        # prices= response.xpath('//sapn[@class="price ng-binding"]/text()').re(r'[\d.,]+')
        # if prices:
        #     item['Product Price'] = prices[0]
        # else:
        #     item['Product Price'] = ''
        #
        # item['Product Price Currency'] = 'SGD'
        # item['Product Description'] = response.xpath('//div[@class="overview ng-binding"]/text()').extract_first()
        # categories = response.xpath('//p[@class="breadcrumbs"]/span/a/text()').extract()
        # if categories:
        #     categories = categories[:-1]
        #     item['Product Category'] = '/'.join(categories)
        # else:
        #     item['Product Category'] = ''
        #
        #
        # item['Image URL'] = response.xpath('//img[@id="productimg"]/@src').extract_first()
        # if item['Image URL']:
        #     item['Image URI'] = item['Image URL'].split('/')[-1]
        # item['Product URL'] = response.url
        #
        # yield item


