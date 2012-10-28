#!/usr/bin/env python
# encoding: utf-8
"""
WillhabenObserver.py

Created by Martin Hammerschmied on 2012-09-09.
Copyright (c) 2012. All rights reserved.
"""
import time
from itertools import compress
from WillhabenConnector import *
from Logger import *
import threading

class WillhabenObserver(threading.Thread):
    
    def __init__(self, url, store, assessor, notification, logger = Logger(), update_interval = 180):
        super(WillhabenObserver, self).__init__()
        self.interval = update_interval
        self.connector = WillhabenConnector(url)
        self.store = store
        self.assessor = assessor
        self.notification = notification
        self.logger = logger
        self.daemon = True
    
    def process_ads(self, ads):
        hits = map(self.assessor.check, ads)
        hit_ads = [ad for ad in compress(ads, hits)]
        new_ads = self.store.add_ads(hit_ads)
        for ad in new_ads:
            self.logger.append("Observer Found Ad: " + ad["title"])
            if self.notification:
                self.notification.notifyAll(title = "Willhaben Ad spotted!", subtitle = "€ " + str(ad["price"]), text = ad["title"], url = ad["url"])

    def run(self):
        # TODO: don't initialize on number of pages but on ad date!!
        self.logger.append("Observer polling 10 pages")
        ads = self.connector.all_ads(maxpages = 10)
        self.process_ads(ads)
        self.logger.append("Initial poll done")
        while True:
            time.sleep(self.interval)
            self.logger.append("Observer polling front page")
            try:
                frontpage_ads = self.connector.frontpage_ads()
                self.process_ads(frontpage_ads)
            except WillhabenConnectionError:
                self.logger.append("No connection to willhaben.at")