# -*- coding: utf-8 -*-
import scrapy


class SundanceFilmsSpider(scrapy.Spider):
    name = 'sundance_films'
    allowed_domains = ['www.sundance.org']

    def start_requests(self):
        yield scrapy.Request(url='https://www.sundance.org/2020-sundance-film-festival-program-guide/DOC-guide',
                             callback=self.parse,
                             )

    def parse(self, response):
        links = response.css('.card-content .title a')
        for link in links:
            suffix = link.xpath('@href').extract_first()
            url = "https://www.sundance.org" + suffix
            yield scrapy.Request(url=url, callback=self.parse_film_data
                                )

    def parse_film_data(self, response):
        items = {}
        title = response.css('h1::text').extract_first().strip()
        #synopsis = response.css('.about p:nth-child(3)::text').extract_first()
        country = response.css('p:nth-child(8)::text').extract_first().strip()
        run_time = response.css('p:nth-child(9)::text').extract_first().strip()
        language = response.css('p:nth-child(10)::text').extract_first().strip()
        website = response.css('p:nth-child(13) a::text').extract_first()
        email = response.css('p:nth-child(14) a::text').extract_first()
        phone = response.css('p:nth-child(15)::text').extract_first()
        directors = response.css('.director_credits a::text').extract()
        producers = response.css('.producers_credits a::text').extract()
        if not producers:
            producers = response.css('.produced_by_credits a::text').extract()
            if not producers:
                producers = response.css('.producer_credits a::text').extract()
        about = response.css('.border.about p')
        synopsis = about[1].css('::text').extract_first()
        items["title"] = title
        items["synopsis"] = synopsis
        #items["country"] = country
        #items["run_time"] = run_time
        #items["language"] = language
        #items["website"] = website
        #items["email"] = email
        #items["phone"] = phone
        for data in about:
            data_list = data.css('::text').extract()
            if 'COUNTRY' in data_list:
                items["country"] = data_list[1].strip()
            if 'PHONE' in data_list:
                items["phone"] = data_list[1].strip()
            if 'RUN TIME' in data_list:
                items["run_time"] = data_list[1].strip()
            if 'LANGUAGE' in data_list:
                items["language"] = data_list[1].strip()
            if 'WEBSITE' in data_list:
                items["website"] = data_list[2].strip()
            if 'EMAIL' in data_list:
                items["email"] = data_list[2].strip()
        items["directors"] = directors
        items["producers"] = producers
        yield items
















