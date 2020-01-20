# -*- coding: utf-8 -*-
import scrapy


class TrecTexasSpider(scrapy.Spider):
    name = 'trec_texas'
    allowed_domains = ['www.trec.texas.gov']
    count = 1

    def start_requests(self):
        yield scrapy.Request(url='https://www.trec.texas.gov/apps/license-holder-search/?lic_name=&industry=Inspectors&email=&city=&county=&zip=&display_status=&lic_hp=&ws=858&license_search=Search',
                             callback=self.parse,
                             )

    def parse(self, response):
        links = response.css('.panel-title a')
        for link in links:
            suffix = link.xpath('@href').extract_first()
            url = "https://www.trec.texas.gov/apps/license-holder-search/" + suffix
            yield scrapy.Request(url=url, callback=self.parse_inspect_data
                                 )
        next_url_suffix = response.css('.next a').xpath('@href').extract_first()
        next_url = response.urljoin(next_url_suffix)

        if self.count < 3:
            yield scrapy.Request(url=next_url, callback=self.parse)
            self.count += 1


    def parse_inspect_data(self, response):
        items = {}
        name = response.css('h2::text').extract_first()
        email = ''.join(response.css('#insi-0::text').extract())
        phone = ''.join(response.css('#insi-1::text').extract())
        address = response.css('.data-fluid::text').extract()[3] + " " + response.css('.data-fluid::text').extract()[4]
        items["name"] = name
        items["email"] = email
        items["phone"] = phone
        items["address"] = address
        yield items




