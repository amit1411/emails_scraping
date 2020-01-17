# -*- coding: utf-8 -*-
import scrapy
from scrapy import FormRequest
import re


class LuxurySpider(scrapy.Spider):
    name = 'luxury'
    allowed_domains = ['https://www.luxuryhomemarketing.com']
    area_mapping = {"AK": "Alaska", "AL": "Alabama"}

    def start_requests(self):
        #start_urls = ['https://www.luxuryhomemarketing.com/real-estate-agents/advanced_search.html/']
        area_codes = ['AK', 'AL']
        for area_code in area_codes:
            yield FormRequest(url='https://www.luxuryhomemarketing.com/real-estate-agents/advanced_search.html/',
                              formdata={'Country': 'US/CA', 'State_prov': area_code}, callback=self.parse,
                              meta={"area_code": area_code}, dont_filter=True)

    def parse(self, response):

        links = response.css('a.link-member')
        for link in links:
            suffix = link.xpath('@href').extract_first()
            url = "https://www.luxuryhomemarketing.com" + suffix[2:]
            #url = response.urljoin(link.xpath('@href').extract_first())
            yield scrapy.Request(url=url, callback=self.parse_emails, meta={"area_code": response.meta["area_code"]}
                                 , dont_filter=True)

    def parse_emails(self, response):
        items = {}
        email = response.css('.btn-border').xpath('@href').extract_first()
        name = response.css('.mb0::text').extract_first()
        name = re.sub(r'[^a-zA-Z ]+', '', name).strip()
        email = email.split(":")
        items["Area"] = LuxurySpider.area_mapping[response.meta["area_code"]]
        items["Name"] = name
        items["Email"] = email[1]

        yield items
