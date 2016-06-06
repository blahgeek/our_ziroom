#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Author: BlahGeek
# @Date:   2016-06-05
# @Last Modified by:   BlahGeek
# @Last Modified time: 2016-06-06

import scrapy
from ..items import ZiroomItem

class ZiroomSpider(scrapy.Spider):
    name = 'ziroom'
    allowed_domains = ['ziroom.com', ]
    start_urls = ['http://www.ziroom.com/z/nl/', ]

    def parse(self, response):
        pages = int(response.css('#page span::text').re_first(r'[0-9]+'))
        self.logger.info('{} pages found'.format(pages))
        for x in range(1, pages+1):
            yield scrapy.Request(response.urljoin('?p={}'.format(x)),
                                 callback=self._parse_page,
                                 meta={'dont_cache': True})

    def _parse_page(self, response):
        for room in response.css('#houseList > .clearfix:not(.zry)'):
            url = response.urljoin(room.css('.txt h3 a::attr(href)').extract_first())
            yield scrapy.Request(url, callback=self._parse_detail)

    def _parse_detail(self, response):
        item = ZiroomItem()
        item['url'] = response.url
        item['title'] = response.css('.room_name h2::text').extract_first().strip()
        item['location'] = response.css('.room_name .pr::text').extract_first().strip()

        infos = response.css('.detail_room li::text')
        item['area'] = infos.re_first(r'([0-9\.]+)㎡')
        item['floor'] = infos.re_first(r'([0-9]+/[0-9]+)层')
        item['layout'] = infos.re_first(r'[0-9]+室[0-9]厅+')
        if item['area']:
            item['area'] = float(item['area'])

        item['subway_info'] = response.css('#lineList::text').extract_first()
        if item['subway_info']:
            item['subway_info'] = item['subway_info'].strip()
        item['tags'] = response.css('.detail_room span.icons::text').extract()
        item['tags'] += response.css('.room_tags span::text').extract()
        item['price'] = int(response.css('.room_price::text').re_first(r'[0-9]+'))

        item['lon'] = response.css('#mapsearchText::attr(data-lng)').extract_first()
        item['lat'] = response.css('#mapsearchText::attr(data-lat)').extract_first()

        return item
