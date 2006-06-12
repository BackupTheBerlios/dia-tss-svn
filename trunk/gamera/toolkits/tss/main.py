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

def drawFoundLines(max, width, height, output_image):
    """Draws the lines dependent on theta and rho of the found maximas."""
    yCoord = 0
    image = Image((0, 0), Dim(width, height), ONEBIT, DENSE)
    
    for x in max:
        pixelValue = x[0]
        theta = x[1]
        rho = x[2]
        rTheta = (theta * pi) / 180
        print "theta = %f" %theta, " rho = %f" %rho
        if rTheta == 0 and rho > 0:
            for y in range(image.nrows-1):
                image.set( (rho, y), 1 )
        for i in range(image.ncols-1):
            if rTheta > 0:
                yCoord = (rho / sin(rTheta)) - ( i * ( cos(rTheta) / sin(rTheta) ) )
                if int(abs(yCoord)) < image.nrows-1:
                    image.set( (i, int(abs(yCoord))), 1 )

    image.save_PNG( r"%s"%output_image )

def calcMax(img):
    """Searches for maxima in Hough-Space. When found, stores the pixelvalue and the x/y-coordinates."""
    max = []
    temp_max = (0.0,0,0)
    maxima = 0.0

    for x in range(5):
        for y in range(img.nrows):
            if maxima < img.get((x,y)):
                maxima = img.get((x, y))
                if maxima > 20:
                    temp_max = (maxima, x, y)
                    print temp_max
                    max.append(temp_max)

    maxima = 0.0

    for x in range(85,95):
        for y in range(img.nrows):
            if maxima < img.get((x, y)):
                maxima = img.get((x, y))
                if maxima > 20:
                    temp_max = (maxima,x,y)
                    print temp_max
                    max.append(temp_max)

    maxima = 0.0

    for x in range(175,180):
        for y in range(img.nrows):
            if maxima < img.get((x, y)):
                maxima = img.get((x, y))
                if maxima > 20:
                    temp_max = (maxima,x,y)
                    print temp_max
                    max.append(temp_max)

    return max

def calcAvgHeight(ccs):
    avg_height = 0
    
    for i in ccs:
        avg_height += i.nrows
    avg_height /= len(ccs)

    return avg_height


def main():
    if len(argv) != 3:
        print "to few arguments in call to %s" %argv[0]
        print "usage: %s input.png output.png" %argv[0]
        exit(-1)
    init_gamera()
    from gamera.toolkits import tss
    input_image = argv[1]
    output_image = argv[2]
    image0 = load_image(r"%s"%input_image)
    onebit0 = image0.to_onebit()
    print "Performing area ratio filter..."
    ccs = onebit0.area_ratio_filter()
    avg_height = calcAvgHeight(ccs)
    print "Average Heigth = ", avg_height
    print "Performing hough transformation..."
    floatImage = tss.plugins.TextStringSep.hough_transform(ccs, [0.0,0.5,85.0,95.0,175.0,185.0], (0.2 * avg_height), 1.0, onebit0.ncols, onebit0.nrows)
    print "Calculate maximas..."
    max = calcMax( floatImage )
    print "maximas: ", max
    print "Draw found lines..."
    drawFoundLines( max, onebit0.ncols, onebit0.nrows, output_image )
