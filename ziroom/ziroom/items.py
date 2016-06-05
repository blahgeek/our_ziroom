#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Author: BlahGeek
# @Date:   2016-06-05
# @Last Modified by:   BlahGeek
# @Last Modified time: 2016-06-05

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZiroomItem(scrapy.Item):
    title = scrapy.item.Field()
    location = scrapy.item.Field()
    area = scrapy.item.Field()
    floor = scrapy.item.Field()
    layout = scrapy.item.Field()
    subway_info = scrapy.item.Field()
    tags = scrapy.item.Field()
    price = scrapy.item.Field()
