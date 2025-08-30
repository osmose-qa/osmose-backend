#!/usr/bin/env python

import requests
import sys

import osmose_config

main_url = 'http://polygons.openstreetmap.fr/'
relation_generation_url = main_url + 'index.py'
polygon_union_url = main_url + 'get_poly.py'

fails = []
for c in osmose_config.config.values():
    if not hasattr(c, 'polygon_id'):
        continue
    if not c.polygon_id:
        continue

    print('  ', c.country, c.polygon_id)

    # polygon_id can be an integer, or a list of integers
    polygon_id = c.polygon_id
    if isinstance(polygon_id, int):
        polygon_id = (polygon_id, )

    # generate relation boundary
    relation_failing = False
    for poly_id in polygon_id:
        try:
            r = requests.post(relation_generation_url, params={'id': str(poly_id)}, data={'refresh': 1}, timeout=120)
        except requests.exceptions.Timeout:
            print("      Timeout")
            fails.append([c.country, polygon_id, 'Timeout'])
            relation_failing = True
            continue
        if r.status_code == 500:
            print("      Geom Error -", r.url)
            fails.append([c.country, polygon_id, 'Geom Error'])
            relation_failing = True
            continue
        elif r.status_code != 200:
            print("      Error -", r.url)
            fails.append([c.country, polygon_id, 'Error'])
            relation_failing = True
            continue

    if relation_failing:
        continue

    # get associated poly file
    try:
        poly_id = ",".join(map(str, polygon_id))
        r = requests.get(polygon_union_url, params={'id': poly_id, 'params': '0'}, timeout=120)
    except requests.exceptions.Timeout:
        print("      Poly Timeout")
        fails.append([c.country, polygon_id, 'Poly Timeout'])
        continue
    if r.status_code != 200:
        print("      Bad geom -", r.url)
        fails.append([c.country, polygon_id, 'Bad geom'])

if len(fails) > 0:
    print(fails)
    sys.exit(1)
