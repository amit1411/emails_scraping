# -*- coding: utf-8 -*-
import scrapy
from scraper_api import ScraperAPIClient
client = ScraperAPIClient('adc3d866682a18dad67c04d3bcbc7f1c')


class CycleSpider(scrapy.Spider):
    name = 'cycle'
    # allowed_domains = ['www.cylex-uk.co.uk']

    start_urls = [client.scrapyGet(url='https://www.cylex-uk.co.uk/cities/B')]

    def parse(self, response):
        cities = response.css('.col-sm-4 a::attr(href)').extract()
        for city in cities:
            yield scrapy.Request(client.scrapyGet(url=city), callback=self.parse_city)
        next_urls = response.css('.list-inline a::attr(href)').extract()
        for next_url in next_urls:
            yield scrapy.Request(client.scrapyGet(url=next_url), callback=self.parse_pages)

    def parse_pages(self, response):
        cities = response.css('.col-sm-4 a::attr(href)').extract()
        for city in cities:
            yield scrapy.Request(client.scrapyGet(url=city), callback=self.parse_city)

    def parse_city(self, response):
        categs = response.css('#main .row+ div a::attr(href)').extract()
        for cate in categs:
            yield scrapy.Request(client.scrapyGet(url=cate), callback=self.parse_categories)
        streets = response.css('div+ div .list-inline a::attr(href)').extract()
        for street in streets:
            yield scrapy.Request(client.scrapyGet(url=street), callback=self.parse_street)

    def parse_street(self, response):
        sub_cate = response.css('.col-sm-4 a::attr(href)').extract()
        for cate in sub_cate:
            yield scrapy.Request(client.scrapyGet(url=cate), callback=self.parse_street_links)

    def parse_street_links(self, response):
        companies = response.css('.company-data a::attr(href)').extract()
        for company in companies:
            yield scrapy.Request(client.scrapyGet(url=company), callback=self.parse_data, meta={"URL": company})

    def parse_categories(self, response):
        sub_cate = response.css('.col-sm-4 a::attr(href)').extract()
        for cate in sub_cate:
            yield scrapy.Request(client.scrapyGet(url=cate), callback=self.parse_links)

    def parse_links(self, response):
        links = response.css('.h4 a::attr(href)').extract()
        for link in links:
            yield scrapy.Request(client.scrapyGet(url=link), callback=self.parse_data, meta={"URL": link})

        # Do Pagination
        next_page = response.css('.pagination a::attr(href)').extract_first()
        if next_page:
            yield scrapy.Request(client.scrapyGet(url=next_page), callback=self.parse_links)

    def parse_data(self, response):
        items = {"Name": "NA", "Official Name": "NA", "Company Number": "NA", "Jurisdiction": "NA",
                 "Previous Names": "NA", "SIC code": "NA", "Incorporation Date": "NA",
                 "Company Type": "NA", "Street": "NA",
                 "Postal": "NA", "Locality": "NA", "Region": "NA", "Latitude": "NA", "Longitude": "NA", "Phone": "NA",
                 "Mobile": "NA", "Fax": "NA", "Website": "NA", "Email": "NA", "Products": "NA", "Service": "NA",
                 "Keyword": "NA", "Brands": "NA", "Service Areas": "NA", "Contact Person": "NA", "Contact Phone": "NA",
                 "Facilities": "NA", "Breadcrumbs": "NA", "Payment Methods": "NA", "Social Media": "NA",
                 "Categories": "NA", "Thursday": "NA",
                 "Friday": "NA", "Saturday": "NA", "Sunday": "NA", "Monday": "NA", "Tuesday": "NA", "Wednesday": "NA",
                 "URL": "NA"}
        #items = {}
        name = response.css('#address span[itemprop=name]::text').extract()
        street = response.css('#primary-address span[itemprop=streetAddress]::text').extract_first()
        post = response.css('#primary-address span[itemprop=postalCode]::text').extract_first()
        local = response.css('#primary-address span[itemprop=addressLocality]::text').extract_first()
        region = response.css('#primary-address span[itemprop=addressRegion]::text').extract_first()
        ph_fax = response.css('.contact-data .hidden-xs')
        email = response.css('#moreEmails span a::attr(href)').extract_first()
        email_2 = response.css('.col-sm-8 a[title="Send message"]::attr(href)').extract_first()
        contact = response.css('.pers-name::text').extract_first()
        contact_phone = response.css('.text-underline p::text').extract()
        latitude = response.css('meta[property="og:latitude"]::attr(content)').extract_first()
        longitude = response.css('meta[property="og:longitude"]::attr(content)').extract_first()
        items["Latitude"] = latitude
        items["Longitude"] = longitude
        if contact_phone:
            items["Contact Phone"] = contact_phone
        if contact:
            contact = contact.replace(u'\xa0', u' ')
            items["Contact Person"] = contact
        if email:
            email = email.split(":")[1].strip()
            items["Email"] = email
        elif email_2:
            email_2 = email_2.split(":")[1].strip()
            items["Email"] = email_2
        try:
            items["Phone"] = ph_fax[0].css('::text').extract()
            items["Mobile"] = ph_fax[1].css('::text').extract()
            items["Fax"] = ph_fax[2].css('::text').extract()
        except IndexError:
            print("---No Fax or Mobile or Phone----")
        web = response.css('.contact-data-url a::attr(title)').extract()
        pay = response.css('.list-unstyled img::attr(title)').extract()
        #social = response.css('#main .col-sm-6 .h4::text').extract()
        social = response.css('.col-sm-6 a[rel=me]::attr(href)').extract()
        if social:
            items["Social Media"] = social
        items["Payment Methods"] = pay
        items["Name"] = name
        items["Street"] = street
        items["Postal"] = post
        items["Locality"] = local
        items["Region"] = region
        items["Website"] = web
        data = response.css('.card-left-padding .h5')
        for i in range(len(data)):
            if "Service" in data[i].xpath('text()').extract_first():
                items["Service"] = data[i].xpath('following::text()').extract_first()
            if "Keyword" in data[i].xpath('text()').extract_first():
                items["Keyword"] = data[i].xpath('following::text()').extract_first()
            if "Facilities" in data[i].xpath('text()').extract_first():
                items["Facilities"] = data[i].xpath('following::text()').extract_first()
            if "Categories" in data[i].xpath('text()').extract_first():
                items["Categories"] = data[i].xpath('following::text()').extract_first()
            if "product" in data[i].xpath('text()').extract_first().lower():
                items["Products"] = data[i].xpath('following::text()').extract_first()
            if "areas" in data[i].xpath('text()').extract_first().lower():
                items["Service Areas"] = data[i].xpath('following::text()').extract_first()
            if "brands" in data[i].xpath('text()').extract_first().lower():
                items["Brands"] = data[i].xpath('following::text()').extract_first()
        categors = response.css('.company-page-breadcrumb')
        allcategors = categors.css('span::text').extract()
        items["Breadcrumbs"] = allcategors
        open_time = response.css('table')
        try:
            rows = open_time[0].css('tr')
            for row in rows:
                open_day = row.css('td span::text').extract()
                if len(open_day) == 3:
                    items[open_day[0].strip()] = open_day[2]
                elif len(open_day) == 4:
                    items[open_day[0].strip()] = open_day[2] + " - " + open_day[-1]
        except IndexError:
            print("---No opening time data it seems..please verify---")
        biz_info = response.css('.biz-info')
        for i in range(len(response.css('.biz-info dt'))):
            if "Official" in biz_info.css('dt')[i].css('::text').extract_first():
                items["Official Name"] = biz_info.css('dd')[i].css('::text').extract_first()
            if "Number" in biz_info.css('dt')[i].css('::text').extract_first():
                items["Company Number"] = biz_info.css('dd')[i].css('::text').extract_first()
            if "Jurisdiction" in biz_info.css('dt')[i].css('::text').extract_first():
                items["Jurisdiction"] = biz_info.css('dd')[i].css('::text').extract_first()
            if "Previous" in biz_info.css('dt')[i].css('::text').extract_first():
                items["Previous Names"] = biz_info.css('dd')[i].css('::text').extract_first()
            if "SIC" in biz_info.css('dt')[i].css('::text').extract_first():
                items["SIC code"] = biz_info.css('dd')[i].css('::text').extract_first()
            if "Incorporation" in biz_info.css('dt')[i].css('::text').extract_first():
                items["Incorporation Date"] = biz_info.css('dd')[i].css('::text').extract_first()
            if "Type" in biz_info.css('dt')[i].css('::text').extract_first():
                items["Company Type"] = biz_info.css('dd')[i].css('::text').extract_first()
        items["URL"] = response.meta["URL"]
        yield items

