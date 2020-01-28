# -*- coding: utf-8 -*-
import scrapy


class CameoMoviesSpider(scrapy.Spider):
    name = 'cameo_movies'
    allowed_domains = ['www.cameo.com']

    def start_requests(self):
        yield scrapy.Request(url='https://www.cameo.com/c/featured',
                             callback=self.parse, dont_filter=True
                             )

    def parse(self, response):
        categories = response.css('.col-md-2 a').xpath('@href').extract()
        for category in categories:
            next_url = response.urljoin(category)
            yield scrapy.Request(url=next_url, callback=self.parse_url, dont_filter=True)

    def parse_url(self, response):
        links = response.css('._3yEJGdKwGboMQH4nTumQvk h4 a').xpath('@href').extract()
        category_name = response.url.split('/c/')[1]
        for link in links:
            url = response.urljoin(link)
            yield scrapy.Request(url=url, callback=self.parse_data, meta={"Category Name": category_name},
                                 dont_filter=True)

    def parse_data(self, response):
        ratings = response.css('#profile-ratings b::text').extract_first()
        name = response.css('#profile-bio-name::text').extract_first().strip()
        items = {}
        items["Name"] = name
        items["Ratings Count"] = ratings
        items["Category"] = response.meta["Category Name"]
        items["URL of Profile"] = response.url
        yield items

