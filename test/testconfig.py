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
from config import ConfigNode, Config

class TestConfigNode(unittest.TestCase):

    def test_config_from_dict(self):
        template =  {
                        'a': 1,
                        'b': {
                            'c': 'test',
                            'd': {
                                'f': 'value'
                            }
                        }
                    }
        config = Config(template)
        self.assertDictEqual(template, config)
        config['x'] = {'new': 'dict'}
        self.assertIs(type(config['x']), ConfigNode)

    def test_illegal_value_type(self):
        class bla: pass
        template = {'a': 1, 'b': bla()}
        def convert():
            Config(template)
        self.assertRaises(TypeError, convert)

    def test_config_path(self):
        value = "Itse meee, Mario!"
        template = {
            'a': {
                'b': {
                    'c': value
                }
            }
        }
        config = Config(template)
        self.assertEqual(value, config.a.b.c)