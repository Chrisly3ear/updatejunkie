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
import base64

from bs4 import BeautifulSoup

from . import base


from datetime import datetime
from enum import Enum

class WillhabenImmoProfile(base.ProfileBase):
    
    name = "WillhabenImmo"
    base_url = "http://www.willhaben.at"
    
    def __init__(self):
        self._tags = {"id":0,
                        "time_found":"",
                        "url":"",
                        "title":"",
                        "size":0,
                        "rooms":0,
                        "price":0.0,
                        "description":"",
                        "location":"",
                        "zipcode":"",
                        "price_p_size":""}
        
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
            query["page"] = [int(query["page"][0]) + 1]
        else:
            query["p"] = 1
        url_components[4] = urllib.parse.urlencode(query, doseq=True)
        return urllib.parse.urlunparse(url_components)

    def parse(self, html):
        soup = BeautifulSoup(html)
        if soup.find(name="div", attrs={"class":"emptySearch"}):
            return list()
        allads = soup.find(name="div", attrs={"id":"resultlist"})
        ads = allads.findAll("article", attrs={"class":"search-result-entry", "itemtype": "http://schema.org/Residence"})
        return list(map(self._ad_soup_to_dict, ads))

    def _ad_soup_to_dict(self, soup):
        tags = self._tags.copy()
        if soup.find(name="div", attrs={"class":"emptySearch"}):
            return tags
        # datetime
        tags["datetime"] = datetime.now()
        tags["time_found"] = tags["datetime"].strftime("%Y-%m-%d %H:%M")
        
        link = soup.find(name="div", attrs={"class":"header"}).find(name="a")
        tags["id"] = int(link.attrs["data-ad-link"])
        tags["url"] = self.base_url + link.attrs['href']

        # Content Feld
        content = soup.find(name="section", attrs={"class":"content-section"})
        #Info Feld
        info = content.find(name="div", attrs={"class":"info"})

        # Groesse u Zimmer
        size_text = info.find('span', attrs={'class':'desc-left'}).text
        try:
            tags["size"] = int(re.findall("[0-9]+", size_text)[0])
        except:
            pass
        try:
            tags["rooms"] = int(re.findall("[0-9]+", size_text)[1])
        except:
            tags["rooms"] = "?"


        # Preis rauswuzeln
        try:
            placeholder_id = info.find(name="div").attrs["id"]
            script = soup.find(name="script")
            regex = placeholder_id+".+?'([^']+)'"
            b64str = re.search(regex, script.text)
            BeautifulSoup(base64.b64decode(b64str.group(1)).decode('UTF-8')).find(name="span").text

            price_text = ".".join(re.findall("[0-9]+", base64.b64decode(b64str.group(1)).decode('UTF-8')))
            if len(price_text) > 0:
                tags["price"] = float(price_text)
        except:
            pass

        if tags["size"] != 0:
            tags["price_p_size"] = '{:.2f}'.format(tags["price"]/tags["size"])

        # Titel
        tags["title"] = soup.find(name="span", attrs={"itemprop":"name"}).text.strip()

        # Beschreibung
        description_text = content.find('div', attrs={'class':'description'}).text
        lines = re.findall("^[\r\n\s]*([^\r^\n]+)[\r\n\s]*", description_text)
        if len(lines) > 0:
            tags["description"] = lines[0]

        
        location_text = content.find('div', attrs={'class':'address-lg'}).text
        lines = re.findall(r'^[\r\n\s]*([^\d^\s][^\r^\n]+)?[\r\n\s]*([0-9]+)[\r\n\s]*([^\r^\n]+)[\r\n\s]*', location_text)
        if len(lines) > 0:
            tags["location"] = " ".join(lines[0])
        
        try:
            tags["zipcode"] = int(re.findall(r'[0-9]{4}', location_text)[0])
        except:
            pass
        
        return tags
