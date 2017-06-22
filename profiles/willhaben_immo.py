#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2012 Martin Hammerschmied

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import re
import urllib.parse
import itertools
import sys
print (sys.version)

from bs4 import BeautifulSoup

from . import base


from datetime import datetime
from enum import Enum

class WillhabenImmoProfile(base.ProfileBase):
    
    name = "WillhabenImmo"
    base_url = "http://www.willhaben.at"
    
    def __init__(self):
        self._tags = {"id":0, "url":"", "title":"", "size":0, "price":0.0, "description":"", "location":"", "zip":0}
        
    @property
    def tags(self):
        return self._tags.keys()

    @property
    def encoding(self):
        return "ISO-8859-1"

    @property
    def key_tag(self):
        return "id"

    @property
    def datetime_tag(self):
        return "datetime"


    def first_page(self, url):
        url_components = list(urllib.parse.urlparse(url))
        query = dict(urllib.parse.parse_qs(url_components[4]))
        query["page"] = 1
        url_components[4] = urllib.parse.urlencode(query, doseq=True)
        return urllib.parse.urlunparse(url_components)

    def next_page(self, url):
        url_components = list(urllib.parse.urlparse(url))
        query = dict(urllib.parse.parse_qs(url_components[4]))
        if "p" in query:
            query["page"] = int(query["page"]) + 1
        else:
            query["p"] = 1
        url_components[4] = urllib.parse.urlencode(query, doseq=True)
        return urllib.parse.urlunparse(url_components)

    def parse(self, html):
        soup = BeautifulSoup(html)
        allads = soup.find(name="div", attrs={"id":"resultlist"})
        ads = allads.findAll("article", attrs={"class":"search-result-entry"})
        #print(ads)
        #ads.extend(allads.findAll("li", attrs={"class":"odd clearfix"}))
        return list(map(self._ad_soup_to_dict, ads))

    def _ad_soup_to_dict(self, soup):
        tags = self._tags.copy()
        print(
            soup

        )
        tags["id"] = int(
            
            soup.find(name="div", attrs={"class":"header"}).find(name="a").attrs["data-ad-link"]
            
            )
        print(tags["id"])
        # tags["url"] = self.base_url + soup.h2.a.attrs['href']        
        # tags["title"] = soup.h2.a.text
        
        # size_text = soup.find('p', attrs={'class':'size'}).text
        # tags["size"] = int(re.findall("[0-9]+", size_text)[0])
        
        # price_text = soup.find('p', attrs={'class':'price'}).text
        # price_text = "".join(re.findall("[0-9]+", price_text))
        # if len(price_text) > 0:
        #     tags["price"] = int(price_text)
        
        # description_text = soup.find('p', attrs={'class':'description'}).text
        # lines = re.findall("^[\r\n\s]*([^\r^\n]+)[\r\n\s]*", description_text)
        # if len(lines) > 0:
        #     tags["description"] = lines[0]
            
        # location_text = soup.find('p', attrs={'class':'location'}).text
        # lines = re.findall("^[\r\n\s]*[0-9]+[\r\n\s]*([^\r^\n]+)[\r\n\s]*", location_text)
        # if len(lines) > 0:
        #     tags["location"] = lines[0]
            
        # zip_text = re.findall("[0-9]+", location_text)[0]
        # tags["zipcode"] = int(zip_text)
        
        return tags
