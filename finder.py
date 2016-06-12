#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Author: BlahGeek
# @Date:   2016-06-05
# @Last Modified by:   BlahGeek
# @Last Modified time: 2016-06-07

import os
import re
import json
import logging
import pickle
import requests
import argparse

class DistanceQuerier:

    API_URL = 'http://api.map.baidu.com/direction/v1'

    def __init__(self, ak, origin, mode, region, cache_file):
        self.params = {
            'ak': ak,
            'origin': origin,
            'mode': mode,
            'region': region,
            'origin_region': region,
            'destination_region': region,
            'output': 'json',
        }
        self.session = requests.Session()
        self.cache_file = cache_file
        if os.path.exists(cache_file):
            self.cache = pickle.load(open(cache_file, 'rb'))
        else:
            self.cache = {}

    def save_cache(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)

    def query(self, destination):
        logging.info('Quering {}->{} ({})'.format(self.params['origin'],
                                                  destination,
                                                  self.params['mode']))
        if destination in self.cache:
            logging.info('Cache hit')
            response = self.cache[destination]
        else:
            logging.info('Cache miss')
            self.params['destination'] = destination
            response = self.session.get(self.API_URL, params=self.params)
            response = response.json()
            assert response['status'] == 0 \
                    and response['message'] == 'ok' \
                    and response['type'] == 2, 'Unable to query distance'
            self.cache[destination] = response
        if self.params['mode'] == 'transit':
            result = response['result']['routes'][0]['scheme'][0]
        else:
            result = response['result']['routes'][0]
        return result['duration'], result['distance']


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Ziroom finder')
    parser.add_argument('--min-price', type=float, help='Min price')
    parser.add_argument('--max-price', type=float, help='Max price')
    parser.add_argument('--min-area', type=float, help='Min area (m^2)')
    parser.add_argument('--max-area', type=float, help='Max area (m^2)')
    parser.add_argument('--layout', help='Layout')
    parser.add_argument('--tag', action='append', help='Required tags')
    parser.add_argument('--distance', action='append', help='Distance requirement. \n' +
                        'Syntax: --distance LOC,minutes[,mode]\n' +
                        '  e.g.  --distance 五道口,30,transit' +
                        '  mode: transit or driving')
    parser.add_argument('--region', help='API region', default='北京')
    parser.add_argument('--ak', help='API ak, required when using --distance')
    parser.add_argument('data', help='Json data crawled by scrapy')
    args = parser.parse_args()

    with open(args.data) as f:
        data = json.load(f)

    if args.min_price is not None:
        data = filter(lambda x: x.get('price', 1e6) >= args.min_price, data)
    if args.max_price is not None:
        data = filter(lambda x: x.get('price', 0) <= args.max_price, data)
    if args.min_area is not None:
        data = filter(lambda x: x.get('area', 1e6) >= args.min_area, data)
    if args.max_area is not None:
        data = filter(lambda x: x.get('area', 0) <= args.max_area, data)
    if args.layout is not None:
        data = filter(lambda x: x.get('layout', '') == args.layout, data)
    if args.tag:
        for tag in args.tag:
            data = filter(lambda x,tag=tag: tag in x.get('tags', []), data)

    data = list(data)
    logging.info("{} left before distance filtering".format(len(data)))

    if args.distance:
        distance_reqs = [{
            'origin': x[0],
            'max_time': float(x[1]), # minutes
            'mode': 'transit' if len(x) <= 2 else x[2]
        } for x in map(lambda x: x.split(','), args.distance)]
    else:
        distance_reqs = []

    def extract_loc(d):
        if 'lon' in d and 'lat' in d:
            return '{},{}'.format(d['lat'], d['lon'])
        else:
            m = re.match(r'(.+)[1-9]居室.*', d['title'])
            assert m is not None, 'No match: {}'.format(d['title'])
            return m.group(1)

    for req in distance_reqs:
        assert args.ak is not None
        cache_file = '.{}.{}.bdcache'.format(req['origin'], req['mode'])
        querier = DistanceQuerier(args.ak, req['origin'], req['mode'], args.region, cache_file)
        for d in data:
            d.setdefault('distance', [])
            try:
                t, _ = querier.query(extract_loc(d))
            except:
                logging.exception('Error querying distance')
                t = 0
            d['distance'].append(t / 60)  # minutes
        querier.save_cache()

        data = [x for x in data if x['distance'][-1] <= req['max_time']]

    for d in data:
        print(d)
