# -*- coding: utf-8 -*-
import scrapy
from media_crawler.items import GunosynewsItem


class GunosySpider(scrapy.Spider):
    name = "gunosy"
    allowed_domains = ["gunosy.com"]
    start_urls = ['https://gunosy.com/categories/7']

    def parse(self, response):
        # start_urlsに存在するリンクを再帰的にクローリング
        for sel in response.css("div.list_content"):
            url = sel.css("div.list_title a::attr('href')").extract_first()
            yield scrapy.Request(url, callback=self.parse)

        # Itemの取得（スクレイピング）
        article = GunosynewsItem()
        article['title'] = response.css('div.article_header_text h1').xpath('string()').extract_first()
        article['url'] = response.url
        article['tag'] = response.css('ul.article_header_tags a::text').extract_first()
        article['date'] = response.css('ul.article_header_lead meta::attr(content)').extract_first()
        article['publisher'] = response.xpath('/html/body/div[7]/div[1]/div[2]/div[2]/ul[1]/li[1]').xpath('string()').extract_first()
        image_list = [response.urljoin(i) for i in response.css('div.article.gtm-click img::attr(data-src)').extract()]
        if not image_list == []:
            article['images'] = image_list
            article['top_image'] = image_list[0]
        else:
            article['top_image'] = 'Not image'
            article['images'] = ['Not image']
        body = ''.join(response.css('div.main.article_main p').xpath('string()').extract()).replace('\n', '')
        body = body.split("元記事を読む")[0]
        article['body'] = body

        yield article
