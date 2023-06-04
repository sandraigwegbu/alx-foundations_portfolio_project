#!/usr/bin/env python3
>>> import json
>>> with open("tlh.json", "r") as f:
...     tlh = json.load(f)
...
>>> tlh_latlng=tlh["results"][0]["geometry"]["location"]
>>> tlh_latlng
{'lat': 6.4416762, 'lng': 7.322024799999999}
>>> tlh_latlng["lat"]
6.4416762
>>> tlh_latlng["lng"]
7.322024799999999
>>> with open("london.json", "r") as f:
...     london = json.load(f)
...
>>> london_latlng=london["results"][0]["geometry"]["location"]
>>> london_latlng
{'lat': 51.5072178, 'lng': -0.1275862}
>>> london_latlng["lat"]
51.5072178
>>> london_latlng["lng"]
-0.1275862
>>>

