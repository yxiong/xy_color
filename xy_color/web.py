#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Apr 28, 2015.

import numpy as np
import os.path
import StringIO
import tornado.ioloop
import tornado.web

from PIL import Image
from xy_python_utils.image_utils import imread, imcast

from color_space_transform import color_space_transform as cst

_this_file_path = os.path.dirname(os.path.realpath(__file__))

settings = {
    "static_path": os.path.join(_this_file_path, "static"),
    "template_path": os.path.join(_this_file_path, "templates"),
}

class MainHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.brightness_range = {
            "min": 0,
            "max": 100,
            "value": "50",   # TODO: compute on the fly.
            "step": 1
        }
        self.contrast_range = {
            "min": 0.0,
            "max": 3.0,
            "value": "1.0",
            "step": 0.1
        }
        self.img_width = 512
        self.img_height = 512

    def get(self):
        self.brightness_range["value"] = self.get_query_argument(
            "brightness", self.brightness_range["value"])
        self.contrast_range["value"] = self.get_query_argument(
            "contrast", self.contrast_range["value"])
        img_src = "generated-img?" + \
                  "brightness=" + self.brightness_range["value"] + "&" + \
                  "contrast=" + self.contrast_range["value"]
        self.render("web.html",
                    img_src = img_src,
                    img_width = self.img_width,
                    img_height = self.img_height,
                    brightness_range = self.brightness_range,
                    contrast_range = self.contrast_range)

class ImageHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.original_image = imread(_this_file_path + "/static/imgs/lenna.png")
        self.original_lab = cst(
            self.original_image, "sRGB", "CIE-L*a*b*")

    def get(self):
        brightness = float(self.get_query_argument("brightness"))
        contrast = float(self.get_query_argument("contrast"))
        adjusted_lab = self.original_lab.copy()
        self.adjust_l_channel(adjusted_lab[:,:,0], brightness, contrast)
        adjusted_image = cst(adjusted_lab, "CIE-L*a*b*", "sRGB")
        adjusted_image[adjusted_image>1.0] = 1.0
        adjusted_image[adjusted_image<0.0] = 0.0
        self.render_image(adjusted_image)

    def render_image(self, img_data):
        img = Image.fromarray(imcast(img_data, np.uint8))
        o = StringIO.StringIO()
        img.save(o, format="JPEG")
        s = o.getvalue()
        o.close()
        self.set_header("Content-type", "image/jpg")
        self.set_header("Content-length", len(s))
        self.write(s)

    def adjust_l_channel(self, l, brightness, contrast):
        l -= np.mean(l)
        l *= contrast
        l += brightness

handlers = [
    (r"/", MainHandler),
    (r"/generated-img", ImageHandler),
]

application = tornado.web.Application(handlers, **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
