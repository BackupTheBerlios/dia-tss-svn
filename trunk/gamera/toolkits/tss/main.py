"""
The main function for the Tss Gamera toolkit

This is a good place for top-level functions, such as things
that would be called from the command line.

This module is not strictly necessary.
"""

from time import sleep
from sys import stdout
from gamera.core import *
from gamera.gui import gamera_display

def main():
    init_gamera()
    from gamera.toolkits import tss
    image0 = load_image(r"/home/olzzen/fh/dia/Namenlos.png")
    onebit0 = image0.to_onebit()
    ccs = onebit0.cc_analysis()
    print "Performing hough transformation..."
    test = tss.plugins.TextStringSep.hough_transform( ccs )
    test.display()
    #    onebit0.area_ratio_filter()
