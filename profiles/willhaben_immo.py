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

from bs4 import BeautifulSoup
from profile import Profile
import re

class WillhabenProfile(Profile):
    
    name = "Willhaben"
    
    def __init__(self):
        self._tags = {"id":0, "url":"", "title":"", "size":0, "price":0.0, "description":"", "location":"", "zipcode":0}
        
    @property
    def tags(self):
        return self._tags.keys()
    
    def parse(self, html):
        soup = BeautifulSoup(html)
        allads = soup.find(name="ul", attrs={"id":"resultlist"})
        ads = allads.findAll("li", attrs={"class":"even clearfix"})
        ads.extend(allads.findAll("li", attrs={"class":"odd clearfix"}))
        return list(map(self.parse_ad, ads))

    def parse_ad(self, soup):
        tags = self._tags.copy()
        tags["id"] = int(soup.h2.attrs['id'])
        tags["url"] = soup.h2.a.attrs['href']        
        tags["title"] = soup.h2.a.text
        
        size_text = soup.find('p', attrs={'class':'size'}).text
        tags["size"] = int(re.findall("[0-9]+", size_text)[0])
        
        price_text = soup.find('p', attrs={'class':'price'}).text
        tags["price"] = int("".join(re.findall("[0-9]+", price_text)))
        
        description_text = soup.find('p', attrs={'class':'description'}).text
        lines = re.findall("^[\r\n\s]*([^\r^\n]+)[\r\n\s]*", description_text)
        if len(lines) > 0:
            tags["description"] = lines[0]
            
        location_text = soup.find('p', attrs={'class':'location'}).text
        lines = re.findall("^[\r\n\s]*[0-9]+[\r\n\s]*([^\r^\n]+)[\r\n\s]*", location_text)
        if len(lines) > 0:
            tags["location"] = lines[0]
            
        tags["zipcode"] = int(re.findall("[0-9]+", location_text)[0])
        
        return tags
    

if __name__ == "__main__":
    from urllib import request
    f = request.urlopen("http://www.willhaben.at/iad/immobilien/eigentumswohnung/wien/wien-1150-rudolfsheim-fuenfhaus/")
    html = f.read()
    f.close()
    
    p = WillhabenProfile()
    ads = p.parse(html)
    print(ads)
    