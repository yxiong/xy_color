#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Apr 28, 2015.

import io
import numpy as np
import os
import tornado.ioloop
import tornado.web

from PIL import Image
from xy_python_utils.image_utils import imread, imcast

_this_file_path = os.path.dirname(__file__)

settings = {
    "static_path": os.path.join(_this_file_path, "static"),
    "template_path": os.path.join(_this_file_path, "templates"),
    "debug": True,
    "gzip": True
}

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        range_value = self.get_query_argument("range", "1.0")
        self.render("web.html",
                    img_src = "generated-img?range=" + range_value,
                    range_value = range_value)

class ImageHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.original_image = imread("static/imgs/lenna.png")

    def get(self):
        range_value = float(self.get_query_argument("range", 1.0))
        adjusted_image = self.original_image * range_value
        adjusted_image[adjusted_image>1.0] = 1.0
        self.render_image(adjusted_image)

    def render_image(self, img_data):
        img = Image.fromarray(imcast(img_data, np.uint8))
        o = io.BytesIO()
        img.save(o, format="JPEG")
        s = o.getvalue()
        self.set_header("Content-type", "image/jpg")
        self.set_header("Content-length", len(s))
        self.write(s)

handlers = [
    (r"/", MainHandler),
    (r"/generated-img", ImageHandler),
]

application = tornado.web.Application(handlers, **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
