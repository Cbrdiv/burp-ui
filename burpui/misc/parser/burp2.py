# -*- coding: utf8 -*-
from .burp1 import Parser as Burp1


# inherit Burp1 parser so we can just override available options
class Parser(Burp1):
    """Implements :class:`burpui.misc.parser.burp1.Parser`"""
    pver = 2
