#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Author: BlahGeek
# @Date:   2016-06-05
# @Last Modified by:   BlahGeek
# @Last Modified time: 2016-06-05

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
                                 callback=self._parse_page)

    def _parse_page(self, response):
        for room in response.css('#houseList > .clearfix:not(.zry)'):
            item = ZiroomItem()
            item['title'] = room.css('.txt h3 a::text').extract_first().strip()
            item['location'] = room.css('.txt h4 a::text').extract_first().strip()

            infos = room.css('.txt .detail span:not(.icons)::text')
            item['area'] = infos.re_first(r'([0-9\.]+)㎡')
            item['floor'] = infos.re_first(r'[0-9]+/[0-9]+')
            item['layout'] = infos.re_first(r'[0-9]+室[0-9]厅+')
            if item['area']:
                item['area'] = float(item['area'])

            item['subway_info'] = infos.extract()[-1]
            item['tags'] = room.css('.txt .detail span.icons::text').extract()
            item['tags'] += room.css('.txt .room_tags span::text').extract()
            item['price'] = int(room.css('.price::text').re_first(r'[0-9]+'))

            yield item
