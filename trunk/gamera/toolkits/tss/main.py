"""
The main function for the Tss Gamera toolkit

This is a good place for top-level functions, such as things
that would be called from the command line.

This module is not strictly necessary.
"""

from time import sleep
from sys import stdout
from gamera.core import *


def main():
    init_gamera()
    from gamera.toolkits import tss
    image0 = load_image(r"/home/pragma/Bilder/Document Imaga Analysys/230 hub diag.png")
    onebit0 = image0.to_onebit()
    onebit0.area_ratio_filter()
