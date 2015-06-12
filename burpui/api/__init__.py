# -*- coding: utf8 -*-
"""
.. module:: api
   :platform: Unix
   :synopsis: Burp-UI api module.

.. moduleauthor:: Ziirish <ziirish@ziirish.info>


"""
import os
import re

from burpui import app
from flask.ext.restful import Api

api = Api(app)

app.jinja_env.globals.update(api=api)

# hack to automatically import api modules
for f in os.listdir(__path__[0]):
    name, ext = os.path.splitext(f)
    if (os.path.isfile(os.path.join(__path__[0], f)) and
            ext == '.py' and
            name not in ['__init__', '.', '..']):
        mod = 'burpui.api.' + f[:-3]
        __import__(mod)
