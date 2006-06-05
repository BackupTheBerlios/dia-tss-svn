"""
The main function for the Tss Gamera toolkit

This is a good place for top-level functions, such as things
that would be called from the command line.

This module is not strictly necessary.
"""

from time import sleep
from sys import stdout, argv, exit
from cmath import *
from gamera.core import *
from gamera.gui import gamera_display

def drawFoundLines(max, width, height, img):
    """Draws the lines dependent on theta and rho of the found maximas."""
    image = Image((0, 0), Dim(width, height), ONEBIT, DENSE)
    
    for x in max:
        pixelValue = x[0]
        theta = x[1]
        rho = x[2]
        rTheta = ( theta * pi) / 180
        print "theta = %f" %theta, " rho = %f" %rho
        for i in range(image.ncols-1):
            yCoord = (rho / sin(rTheta)) - ( i * ( cos(rTheta) / sin(rTheta) ) )
            if int(abs(yCoord)) < image.nrows-1:
                #print "x = ", i, " y = ", int(abs(yCoord))
                image.set( (i, int(abs(yCoord))), 1 )

    image.save_PNG(r"/home/olzzen/fh/6sem/dia/output1.png")

def calcMax(img):
    """Searches for maxima in Hough-Space. When found, stores the pixelvalue and the x/y-coordinates."""
    max = [(0.0,0,0),(0.0,0,0),(0.0,0,0)]
    maxima = 0.0

    for x in range(5):
        for y in range(img.nrows):
            if maxima < img.get((x,y)):
                maxima = img.get((x, y))
                max[0] = (maxima, x, y)

    maxima = 0.0

    for x in range(85,95):
        for y in range(img.nrows):
            if maxima < img.get((x, y)):
                maxima = img.get((x, y))
                max[1] = (maxima, x, y)

    maxima = 0.0

    for x in range(175,180):
        for y in range(img.nrows):
            if maxima < img.get((x, y)):
                maxima = img.get((x, y))
                max[2] = (maxima, x, y)

    return max


def main():
    if len(argv) != 3:
        print "to few arguments in call to %s" %argv[0]
        print "usage: %s input.png output.png" %argv[0]
        exit(-1)
    init_gamera()
    from gamera.toolkits import tss
    image0 = load_image(r"/home/olzzen/fh/6sem/dia/NurText.png")
    onebit0 = image0.to_onebit()
    print "Performing area ratio filter..."
    ccs = onebit0.area_ratio_filter()
    print "Performing hough transformation..."
    floatImage = tss.plugins.TextStringSep.hough_transform(ccs, [0.0,5.0,85.0,95.0,175.0,180.0], 1, 0.2, onebit0.ncols, onebit0.nrows)
    print "Calculate maximas..."
    max = calcMax( floatImage )
    image1 = load_image(r"/home/olzzen/fh/6sem/dia/output.png")
    print "Draw found lines..."
    drawFoundLines( max, image1.ncols, image1.nrows, image1 )
