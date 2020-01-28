# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest


class PharmSpider(scrapy.Spider):
    name = 'pharm'
    allowed_domains = ['www.pharmasuisse.org']

    run_script = """
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(0.5))
  splash:evaljs('document.querySelector(".link-email").click()')
  return {
    html = splash:html()
  }
end
                    """
    #splash:evaljs('document.querySelector(".link-email").click()')
    splash_request_args = {"lua_source": run_script}


    def start_requests(self):
        start_urls = ['https://www.pharmasuisse.org/de/1364/Apothekenfinder.htm?DatasourcePage={0}&cmsOutput=nodesign' \
                      '&DatasourceName=PharmacyList&cmsBrick=1'
                      '&FilterData%5BTypeaheadData-PharmacyList-Fulltext%5D%5BFulltext%5D=&pc3AjaxContent' \
                      '=grid-load-more-PharmacyList'.format(page) for page in
                      range(1, 2)]
        for url in start_urls:
            yield scrapy.Request(url=url,
                                 callback=self.parse_url
                                 )

    def parse_url(self, response):
        links = response.css('.link-overlay-initialize::attr(href)').extract()
        for link in links:
            yield SplashRequest(url=link, callback=self.parse_data,
                                args=self.splash_request_args, endpoint='execute')

    def parse_data(self, response):
        items = {}
        name = response.css('.typo-text-copy-emphasize::text').extract_first().strip()
        text = response.css('.typo-text-copy::text').extract()
        street = text[0].strip()
        pin_code = text[1].split()[0]
        city = text[1].split()[1]
        phone = text[3].strip()
        fax = text[4].strip()
        email = response.css('.link-email::attr(href)').extract_first().split(':')[1].strip()
        if len(response.css('.link-external::attr(href)').extract()) == 2:
            website = response.css('.link-external::attr(href)').extract()[0].strip()
        else:
            website = "NA"
        items["Name"] = name
        items["Street"] = street
        items["Pin Code"] = pin_code
        items["City"] = city
        items["Phone"] = phone
        items["Fax"] = fax
        items["Email"] = email
        items["Website"] = website
        yield items









