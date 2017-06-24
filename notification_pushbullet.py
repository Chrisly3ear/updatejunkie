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

import time

import json
import requests
from requests.auth import HTTPBasicAuth

from notifications import Notification


class PushbulletNotification(Notification):
    """
    Sends PushBullet notification using python's pushbullet.py module
    """

    def __init__(self, api, subject, body):
        self._api_url = "https://api.pushbullet.com/v2"
        self._api_key = api
        self._subject = subject
        self._body = body

    def _request(self, method, url, postdata=None, params=None, files=None):
        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "User-Agent": "pyPushBullet"}

        if postdata:
            postdata = json.dumps(postdata)
        
        # Reduce logging spam
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        res = requests.request(method,
                               url,
                               data=postdata,
                               params=params,
                               headers=headers,
                               files=files,
                               auth=HTTPBasicAuth(self._api_key, ""))
        
        res.connection.close()
        #res.raise_for_status() # Don't care
        retval = res.json()
        retval["headers"] = res.headers
        return retval

    def _push_note(self, title, body, recipient=None, recipient_type="device_iden"):
        """ Push a note
            https://docs.pushbullet.com/v2/pushes
            Arguments:
            title -- a title for the note
            body -- the body of the note
            recipient -- a recipient (all devices if omitted)
            recipient_type -- a type of recipient (device, email, channel or client)
        """

        data = {"type": "note",
                "title": title,
                "body": body}

        data[recipient_type] = recipient

        return self._request("POST", self._api_url + "/pushes", data)

    def _get_push_history(self, active=True, modified_after=0, limit=None, cursor=None):
        """ Get Push History
            https://docs.pushbullet.com/v2/pushes
            Returns a dictionary of "pushes" and a possible "cursor"
            Arguments:
            active -- Don't return deleted/dismissed pushes
            modified_after -- Request pushes modified after this timestamp
            limit -- Limit pushes per page (paginated results)
            cursor -- Request another page of pushes (if necessary)
        """
        data = {"modified_after": modified_after}
        if active:
            data['active'] = "true"
        if limit:
            data["limit"] = limit
        if cursor:
            data["cursor"] = cursor

        response = self._request("GET", self._api_url + "/pushes", None, data)
        return response

    def _compare_title_and_body(self, push, title=None, body=None):

        if "title"in push and "body" in push:
            return push["title"] == title and push["body"] == body
        elif "title"in push:
            return push["title"] == title and body is None
        elif "body" in push:
            return push["body"] == body and title is None
        return False

    def notify(self, ad):
        try:

            logging.debug("Sending notification to Pushbullet")
            title = self._subject.format(**ad)
            body = self._body.format(**ad)
            history = self._get_push_history(limit=1) # Avoid sending notifications twice in a row!
            remain_ratelim = 0
            if "X-Ratelimit-Remaining" in history["headers"]:
                remain_ratelim = int(history["headers"]["X-Ratelimit-Remaining"])
            if "X-Ratelimit-Reset" in history["headers"]:
                ratelim_reset = int(history["headers"]["X-Ratelimit-Reset"])
            if "pushes" in history:
                pushes = list(history["pushes"])

                alrdy_pushed = list(
                                filter(
                                    lambda psh: self._compare_title_and_body(psh, title, body),
                                    pushes))
            
            reset_in = ratelim_reset - time.time()
            m, s = divmod(reset_in, 60)
            h, m = divmod(m, 60)
            if remain_ratelim == 0:
                logging.error("CANNOT SEND NOTIFICATION! Rate limit reached. Can send again in "+ "%d:%02d:%02d" % (h, m, s))
            elif remain_ratelim < 1000:
                self._push_note("Approaching Rate Limit!", "Remaining: "+ "{:,}".format(remain_ratelim) + \
                                                          "\nReset in: " + "%d:%02d:%02d" % (h, m, s))


            if remain_ratelim > 0 and not alrdy_pushed:
                self._push_note(title, body)
                logging.debug("Notification to Pushbullet sent")
            elif remain_ratelim > 0:
                logging.debug("Notification to Pushbullet has already been sent. Not sending again.")
        except Exception as error:
            logging.error("Failed to send notification: {}".format(error.args))

    def serialize(self):
        return {"type": "pushbullet", "api": self._api_key}
