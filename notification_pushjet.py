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

import logging

import json
import requests
from requests.auth import HTTPBasicAuth

from notifications import Notification


class PushjetNotification(Notification):
    """
    Sends PushBullet notification using python's pushbullet.py module
    """

    def __init__(self, secret, title, body, level):
        self._api_url = "https://api.pushjet.io"
        self._secret = secret
        self._title = title
        self._body = body
        self._level = level

    def _request(self, method, url, postdata=None, params=None, files=None):
        headers = {"Accept": "application/json",
                   "Content-Type": "application/x-www-form-urlencoded",
                   "User-Agent": "WillHabenCrawler"}
        
        # Reduce logging spam
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        res = requests.request(method,
                               url,
                               data=postdata,
                               params=params,
                               headers=headers,
                               files=files)
        
        res.connection.close()
        res.raise_for_status() # Don't care
        retval = res.json()
        retval["headers"] = res.headers
        return retval

    def _push_note(self, title, body, link=None):
        """ Push a note
            http://docs.pushjet.io
            Arguments:
            title -- a title for the note
            body -- the body of the note
            link -- optional
            recipient -- a recipient (all devices if omitted)
            recipient_type -- a type of recipient (device, email, channel or client)
        """
        data = {"secret": self._secret,
                "message": body,
                "title": title,
                "level": self._level}

        if link:
            data["link"] = link

        return self._request("POST", self._api_url + "/message", data)

    def notify(self, ad):
        try:

            logging.debug("Sending notification to Pushjet")
            title = self._title.format(**ad)
            body = self._body.format(**ad)
            link = None
            if "url" in ad:
                link = ad["url"]

            if not "pushed" in ad:
                ad["pushed"] = True
                self._push_note(title, body, link)
                logging.debug("Notification to Pushjet sent")
            else:
                logging.debug("Notification to Pushjet has already been sent")
        except Exception as error:
            logging.error("Failed to send notification: {}".format(error.args))

    def serialize(self):
        return {"type": "pushjet", "secret": self._secret}
