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

import unittest
from datetime import datetime
from notifications import *


class TestEmailNotification(unittest.TestCase):
    
    def setUp(self):
        self._ads = [
            dict(datetime = datetime.now(), title="T1", price=3.5, url="http://wer.wo.was.org"),
            dict(datetime = datetime.now(), title="Titolo", price=301.0, url="http://wer.wo.wie.org"),
            dict(datetime = datetime.now(), title="Schraeg", price=0.1, url="http://blind.oder.was.it"),
        ]

    def test_MIME_string_generation(self):
        sender = "Gustl Hemmer <gustl@example.com>"
        to = "Moatl Hemmer <moatl@example.com>"
        mimetype = "text/plain"
        subject = "$Rückenschmerzen sind öfters schlächt$"
        body = "{datetime}{title}€{price}{url}"
        notification = EmailNotification(host = None, port = 25, user = None, 
                          pwd = None, sender = sender, to = to,
                          mimetype = mimetype, subject = subject, body = body)
        for ad in self._ads:
            notification._get_mail(ad, to)