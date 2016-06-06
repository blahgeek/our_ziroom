#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Author: BlahGeek
# @Date:   2016-06-06
# @Last Modified by:   BlahGeek
# @Last Modified time: 2016-06-06

import json
import scrapy
from ..items import ZiroomSubletItem

from .ziroom import ZiroomSpider


class ZiroomSubletSpider(ZiroomSpider):
    name = 'ziroom_sublet'
    _base_url = 'http://www.ziroom.com/event/?_p=ziroomer&_a=ajaxexpress&p={}&s={}'

    def start_requests(self):
        yield scrapy.Request(self._base_url.format(1, 1),
                             callback=self._parse_page,
                             meta={
                                'dont_cache': True,
                                'p': 1,
                                's': 1,
                             })

    def _parse_page(self, response):
        data = json.loads(response.body.decode('utf-8'))
        assert data['msg'] == '操作成功', 'Invalid json response'

        content_list = data['content']['list']
        if content_list == False:
            content_list = []

        for content in content_list:
            yield scrapy.Request(response.urljoin('/z/vr/{}.html'.format(content['id'])),
                                 callback=self._parse_detail_sublet,
                                 meta={'subletinfo': content})
        if content_list:
            s = response.meta['s'] + 1
            p = response.meta['p']
            if s > 3:
                s = 1
                p += 1
            yield scrapy.Request(self._base_url.format(p, s),
                                 callback=self._parse_page,
                                 meta={
                                    'dont_cache': True,
                                    'p': p,
                                    's': s,
                                 })

    def _parse_detail_sublet(self, response):
        item = ZiroomSubletItem(self._parse_detail(response))
        content = response.meta['subletinfo']
        item['sublet_person'] = content.get('customer_name', '')
        item['sublet_contact'] = content.get('customer_tel', '')
        item['sublet_description'] = content.get('room_con', '')
        item['lease_date'] = content.get('lease_date', None)

        return item
