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

from queue import Queue, Empty
from command import CommandError
from api.webapi import WebApi
from config import Config
from threading import Thread
import logging
import time

class ServerError(Exception):pass


class Server(Thread):
    
    def __init__(self):
        super(Server, self).__init__()
        self._config = self._create_config()
        self._observers = list()
        self._command_queue = Queue()
        self._quit = False
        self._web_api = None
        self.name = "Server"

    def _create_config(self):
        """
        These are all available config values. The configuration is fixed. New values can not be added afterwards.
        """
        return Config({
            'smtp': {
                'host': None,
                'port': None,
                'auth': True,
                'user': None,
                'pwd': None
            },
            'web': {
                'host': 'localhost',
                'port': 8118
            }
        }, fixed=True)

    def add_observer(self, observer):
        if (observer.name in [other.name for other in self._observers]):
            logging.info("Replacing observer '{}' on server".format(observer.name))
            self.remove_observer(observer.name)
        else:
            logging.info("Adding observer '{}' to server".format(observer.name))
            
        self._observers.append(observer)
        observer.start()
    
    def remove_observer(self, name):
        try:
            observer = next(observer for observer in self._observers if observer.name == name)
            observer.quit()
            self._observers.remove(observer)
        except StopIteration:
            raise ServerError("No observer with the name of '{}'".format(name))

    def observers(self):
        observer_names = [obs.name for obs in self._observers]
        return observer_names

    def enqueue_command(self, command):
        self._command_queue.put_nowait(command)

    def start_web_api(self):
        host = self._config.web.host
        port = self._config.web.port
        if self._web_api:
            logging.info("Shutting down web API")
            self._web_api.quit()
            self._web_api.join(3)
            if self._web_api.is_alive():
                logging.error("Failed to shut down the web API. Reload failed.")
        logging.info("Starting web API at http://{}:{}".format(host, port))
        self._web_api = WebApi(self, host, port)
        self._web_api.start()

    def register_client(self, client_root, default_file="index.html"):
        if not self._web_api:
            raise ServerError("Web API must be started before a client can be registered")
        self._web_api.register_static_directory(client_root, "", default_file)

    def run(self):
        """
        run() is called after everything is set up. It just waits for commands
        to come in and executes them. Usually commands are put into the queue
        by CommandApis like the WebApi or a JsonScript.
        """
        while True:

            # spin the queue. checking for a quit signal every second
            while True:
                if self._quit:
                    self._shutdown()
                    return
                try:
                    command = self._command_queue.get(block=True, timeout=1)
                    break   # received command!
                except Empty:
                    pass

            # process the command
            command.server = self
            command.condition.acquire()
            try:
                command.response = self._process_command(command)
                command.condition.notify_all()
            finally:
                command.condition.release()

    def quit(self):
        self._quit = True
    
    def __getitem__(self, key):
        if type(key) is not str:
            raise TypeError("The key must be a string containing the observer name.")
        try:
            return next(observer for observer in self._observers if observer.name == key)
        except StopIteration:
            raise KeyError("Observer '{}' not found".format(key))
    
    def __iter__(self):
        return self._observers.__iter__()
    
    def _process_command(self, command):
        try:
            logging.info("Processing command '{}'".format(command.name))
            logging.debug("Command info: {}".format(command._cmd_info))
            response = command.execute()
            response_message = {"status": "OK"}
            response_message["response"] = response
            return response_message
        except (ServerError, CommandError) as ex:
            args_text = "; ".join(["{}".format(arg) for arg in ex.args])
            return {"status": "ERROR", "message": args_text}

    def _shutdown(self):
        logging.info("Shutting down all services")
        if self._web_api:
            self._web_api.quit()
        for observer in self._observers:
            observer.quit()
        if self._web_api:
            self._web_api.join(timeout=3)
            if self._web_api.is_alive():
                logging.warning("Timeout while waiting for web API to shut down")
            else:
                logging.info("Web API successfully shut down")
        for observer in self._observers:
            observer.join(timeout=3)
            if observer.is_alive():
                logging.warning("Timeout while waiting for observer '{}' to shut down".format(observer.name))
            else:
                logging.info("Observer '{}' successfully shut down".format(observer.name))

    @property
    def config(self):
        return self._config
    
    @property
    def command_queue(self):
        return self._command_queue
        