# -*- coding: utf-8 -*-
import scrapy


class WinesSpider(scrapy.Spider):
    name = 'wines'
    allowed_domains = ['winestyle.ru']

    def start_requests(self):
        yield scrapy.Request(url='https://winestyle.ru/wine/1000-1500rub/1500-3000rub/500-1000rub/wines/available/limited_ll/',
                             callback=self.parse,
                             )


    def parse(self, response):
        links = response.css('.title a')
        for link in links:
            suffix = link.xpath('@href').extract_first()
            next_url = response.urljoin(suffix)
            url = "https://www.trec.texas.gov/apps/license-holder-search/" + suffix

            yield scrapy.Request(url=next_url, callback=self.parse_data
                                )

    def parse_data(self, response):
        items = {}
        name = response.css('head title::text').extract_first()
        price = response.css('.right-info .price::text').extract_first().strip()

        ratings = response.css('.rating-text-big meta').xpath('@itemprop').extract()
        ratings_value = response.css('.rating-text-big meta').xpath('@content').extract()
        items["Name"] = name
        items["Price"] = price
        if len(ratings) == 0:
            items["itemReviewed"] = "NA"
            items["worstRating"] = "NA"
            items["ratingValue"] = "NA"
            items["bestRating"] = "NA"
            items["reviewCount"] = "NA"

        if len(ratings) == len(ratings_value):
            n = 0
            while n < len(ratings_value):
                items[ratings[n]] = ratings_value[n]
                n += 1
        details = response.css('.list-description .name::text')
        details_value = response.css('.list-description .links')
        if len(details) == len(details_value):
            m = 0
            while m < len(details_value):
                col_name = response.css('.list-description .name::text')[m].extract()
                col_value = response.css('.list-description .links')[m].css('a::text').extract()
                items[col_name] = col_value
                m += 1
        yield items




