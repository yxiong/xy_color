#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Apr 28, 2015.

import tornado.testing
import tornado.web

import web

class WebTest(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return tornado.web.Application(web.handlers, **web.settings)

    def test_web(self):
        response = self.fetch("/")
        self.assertEqual(response.code, 200)

        response = self.fetch("/non-exists")
        self.assertEqual(response.code, 404)

        response = self.fetch("/generated-img?brightness=20&contrast=1.8")
        self.assertEqual(response.code, 200)
        self.assertTrue(response.headers["Content-Type"].startswith("image"))

if __name__ == "__main__":
    tornado.testing.main()
