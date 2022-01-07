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
    name = "casablanca"
    start_urls = 'http://www.casablanca-bourse.com/bourseweb/Transaction.aspx?Cat=24&amp;IdLink=301'


    def start_requests(self):

        yield Request(self.start_urls , callback=self.parse)


    def parse(self, response):
        # headers = ['Heure', 'Valeur mobilière', 'Cours', 'Quantité', 'Volume']
        headers = response.xpath('//table[@id="arial11bleu"]/tr[2]/td/text()').extract()
        rows = response.xpath('//table[@id="arial11bleu"]//tr[@class="arial11gris"]')
        for row in rows:
            values = row.xpath('.//span[contains(@id, "Transaction1_TransacAction1_RptListTr")]/text()').extract()
            item = OrderedDict()
            for i, val in enumerate(values):
                item[headers[i]] = val.encode('utf8').decode('iso-8859-1', 'ignore').replace(u'\xc2\xa0', ' ')

            yield item


