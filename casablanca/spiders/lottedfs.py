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
    name = "lottedfs"
    start_urls = 'http://eng.lottedfs.com/kr'
    count = 1

    def start_requests(self):

        yield Request(self.start_urls , callback=self.parse)

    def parse(self, response):
        urls = response.xpath('//ul[@id="mainCateInfo"]//dd/a/@href').extract()
        for url_tag in urls:
            # url = url_tag.xpath('./@href').extract_first()
            # category = url_tag.xpath('./text()').extract_first()
            yield Request(response.urljoin(url_tag), self.parseProducts)

    def parseProducts(self, response):
        # urls = response.xpath('//section[@id="prdList"]//li[contains(@class,"productMd")]/div[@class="btnArea"]/a[1]/@data-prd-no').extract()
        catNo = response.body.split('var catNo = "')[-1].split('";')[0]
        catNm = response.body.split('var catNm = "')[-1].split('";')[0]
        dispShopNo = response.body.split('var dispShopNo = "')[-1].split('";')[0]
        url = 'http://eng.lottedfs.com/kr/display/GetPrdList?viewType01=0&lodfsAdltYn=N&catNo={}&catNm={}&dispShopNo={}&sortStdCd=01&brndNoList=&prcRngCd=&genList=&fvrList=&prdAttrCdList=&' \
              'soExclList=&svmnUseRtRngList=&etcFilterList=&cntPerPage=60&curPageNo=1&treDpth=3'.format(catNo, catNm, dispShopNo)
        yield Request(url, self.parseProducts1, meta={'page':1})

    def parseProducts1(self, response):
        urls = response.xpath('//li[contains(@class,"productMd")]/div[@class="btnArea"]/a[1]/@data-prd-no').extract()
        for url in urls:
            yield Request('http://eng.lottedfs.com/kr/product/productDetail?prdNo='+url, self.parseFinal, meta={'id': url})

        current = response.meta['page']
        totalcount = int(response.body.split('var totalCnt = "')[-1].split('"')[0])
        if current*60 < totalcount:
            next = current+1
            url = response.url.replace('curPageNo={}'.format(current), 'curPageNo={}'.format(next))
            yield Request(url, self.parseProducts1, meta={'page': next})

    def parseFinal(self, response):
        item = OrderedDict()
        item['Serial'] = ''
        item['Platform URL'] = 'http://eng.lottedfs.com/kr'
        item['Product Name'] = response.xpath('//meta[@property="rb:itemName"]/@content').extract_first()
        prdOptNo = response.body.split('ProductForm.prdOptNo = "')[-1].split('";')[0]
        prices= response.xpath('//meta[@property="rb:salePrice"]/@content').re(r'[\d.,]+')
        if prices:
            item['Product Price'] = prices[0]
        else:
            item['Product Price'] = ''

        item['Product Price Currency'] = 'USD'
        item['Product Description'] = ''
        categories = response.xpath('//div[@class="navigator product"]//select/option[@selected="selected"]/text()').extract()
        if categories:
            # categories = categories[:-1]
            item['Product Category'] = '/'.join(categories)
        else:
            item['Product Category'] = ''


        item['Image URL'] = response.xpath('//meta[@id="meta_og_image"]/@content').extract_first()
        if item['Image URL']:
            item['Image URI'] = item['Image URL'].split('/')[-1]
        item['Product URL'] = response.url
        item['Serial'] = self.count
        item['Brand'] = response.xpath('//meta[@property="rb:brandName"]/@content').extract_first()
        self.count += 1
        id= response.meta['id']
        url = 'http://eng.lottedfs.com/kr/product/productDetailBtmInfoAjax?prdNo={}&prdOptNo={}&previewYn='.format(id, prdOptNo)
        yield Request(url, self.parseDescription, meta={'item': item, 'id': id}, errback=self.errCall)

    def errCall(self, response):
        yield response.request.meta['item']
    def parseDescription(self, response):
        item = response.meta['item']
        id = response.meta['id']
        trs = response.xpath('//tbody[@name="{}"]/tr'.format(id))
        description = ''
        for tr in trs:
            key = ''.join(tr.xpath('./th//text()').extract())
            val = ''.join(tr.xpath('./td//text()').extract())
            if key == 'Ingredients':
                val = tr.xpath('./td/div/text()').extract_first()
            try:
                row = "{}: {}\n".format(key, val)
                description = description + row
            except:
                continue

        item['Product Description'] = description
        yield item




