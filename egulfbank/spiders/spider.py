import scrapy

from scrapy.loader import ItemLoader

from ..items import EgulfbankItem
from itemloaders.processors import TakeFirst
import requests


payload={}
headers = {
  'Cookie': 'BNES_JSESSIONID=pswb8Xbo4MJqoOtOynnOCvYTfm0ZRI9UQWlpXxI5I0acw2cy+SQnQEFy4t0WEZ270FvgAF6Mkc690W7St2VQv0kPYyUnYzg7GHIP1lzR8RY=; BNES_TAFSessionId=1MDRR9s+wEWONryscYsVW++XW/2E+Cmpl4Tk2nZUn6Pdh6tehoehSxZ66d5bDcpu9CtXb29uVJxUXVG5H5GdfGF9ZSOyy1ZmDSOYcDVIa56e/1XQRVs0ww==; BNES_TAFTrackingId=cc83FX1fB/02/HTlCj9iPiWVo+fqVxNU9JdSaZhHbblOQPmWhN1D5RHUu3YV8x70fkTsG8KgDBQWYitxatR0hZCQmwwBrNqw564hswnC3Tu0+QkL2q3QxQ==; BNES_gbSiteLanguage=jVB+4uVugUZTc8i5k5x8anIzN/8mHRnLTwozpQmHG3/Zm9HGKOweIFQO8umaO+7b; JSESSIONID=A25242BCFB9D317B2EB015F52CEB7491.worker22; TAFSessionId=tridion_1ae9f1ed-da71-4bbc-8990-8f8f2977e015; TAFTrackingId=tridion_a6c5a1de-72dc-4053-b40f-bb3454a087db; gbSiteLanguage=en'
}

class EgulfbankSpider(scrapy.Spider):
	name = 'egulfbank'
	url = "https://www.e-gulfbank.com/en/about-us/media/press-releases/get-list"
	start_urls = ['https://www.e-gulfbank.com/en/about-us/media/press-releases']
	all_pages = []

	def parse(self, response):
		if self.url in self.all_pages:
			return
		data = requests.request("GET", self.url, headers=headers, data=payload)
		data = scrapy.Selector(text=data.text)

		post_links = data.xpath('//div[@class="card-content"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		self.url = 'https://www.e-gulfbank.com' + data.xpath('//a[contains(@data-title,"Next")]/@href').get()
		self.all_pages.append(self.url)
		yield response.follow(response.url, self.parse, dont_filter=True)

	def parse_post(self, response):
		title = response.xpath('//div[@class="news-header"]/h2/text()').get()
		description = response.xpath('//div[@class="article-wrapper"]//text()[normalize-space() and not(ancestor::div[@class="news-header"])]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//p[@class="date"]/text()').get()

		item = ItemLoader(item=EgulfbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
