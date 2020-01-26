# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from scrapy.http import HtmlResponse
from selenium.webdriver.chrome.options import Options


class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['www.csae.com']

    def start_requests(self):
        yield scrapy.Request(url='http://www.csae.com/cvweb/cgi-bin/msascartdll.dll/ProductList?RANGE=1/7&UDEF5QTY=1&wbp=productlist-bookstore.htm&whp=product-bookstore-header.htm&SORT=UDEF2QTY&ONWEBFLG=Y',
                             callback=self.parse,
                             )

    def parse(self, response):
        chromeOptions = Options()
        chromeOptions.add_argument("--kiosk")
        driver = webdriver.Chrome(options=chromeOptions)
        driver.get(response.url)
        time.sleep(4)
        #first_link = self.driver.find_element(By.XPATH, '//*[@id="productLinkTwo1112"]')
        all_links = driver.find_elements_by_xpath("//h4//a")
        for i in range(len(all_links)):
            all_links[i].click()
        #first_link = driver.find_element_by_xpath("//*[@id='productLinkTwo1112']")
        #first_link.click()
            #body = driver.page_source
            #page_response = HtmlResponse(url=driver.current_url, body=body, encoding='utf-8', request=response)
            yield scrapy.Request(url=driver.current_url, callback=self.parse_url)
            driver.back()
            time.sleep(2)
            all_links = driver.find_elements_by_xpath("//h4//a")
        driver.close()
        suffix = response.css('#nextlnk').xpath('@href').extract_first()
        if suffix:
            next_url = response.urljoin(suffix)
            yield scrapy.Request(url=next_url, callback=self.parse)

    def parse_url(self, response):
        url = response.css('.cvContentFrame::attr(src)').extract_first()
        yield scrapy.Request(url=url, callback=self.parse_data)

    def parse_data(self, response):
        title = response.css('h2::text').extract_first().strip()
        nm_price = response.css('#nmprice::text').extract_first()
        m_price = response.css('#mprice::text').extract_first()
        details = response.css('#details').extract_first()
        img_source = response.css('.text-center img::attr(src)').extract_first()
        description = ''.join(response.xpath('//*[@id="details"]/p/text()').extract())
        items = {}
        items["Title"] = title
        items["Non Member Price"] = nm_price
        items["Member Price"] = m_price
        items["Image Source"] = img_source
        items["Format"] = response.css('#details::text').extract()[1]
        if response.css('#details:contains("Copyright")::text').extract():
            if response.css('#details:contains("Dimensions")::text').extract():
                items["Dimensions"] = response.css('#details::text').extract()[3]
                items["Publisher"] = response.css('#details::text').extract()[5]
                items["Copyright"] = response.css('#details::text').extract()[7]
                items["Product Code"] = response.css('#details::text').extract()[9]
            else:
                items["Dimensions"] = "Data Not Available"
                items["Publisher"] = response.css('#details::text').extract()[3]
                items["Copyright"] = response.css('#details::text').extract()[5]
                items["Product Code"] = response.css('#details::text').extract()[7]
        else:
            items["Dimensions"] = response.css('#details::text').extract()[3]
            items["Publisher"] = response.css('#details::text').extract()[5]
            items["Copyright"] = "Data Not Available"
            items["Product Code"] = response.css('#details::text').extract()[7]
        #items["Dimensions"] = response.css('#details::text').extract()[3]
        #items["Publisher"] = response.css('#details::text').extract()[5]
        #items["Product Code"] = response.css('#details::text').extract()[7]
        items["Description"] = description
        yield items




