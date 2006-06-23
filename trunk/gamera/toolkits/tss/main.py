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

def drawFoundLines(max, width, height, output_image, R):
    """Draws the lines dependent on theta and rho of the found maximas."""
    yCoord = 0
    image = Image((0, 0), Dim(width, height), ONEBIT, DENSE)
    
    for x in max:
        pixelValue = x[0]
        theta = x[1]
        rho = x[2]
        rTheta = (theta * pi) / 180
        print "theta = %f" %theta, " rho = %f" %rho
        if ( rTheta == 0 or rTheta == 180) and rho > 0:
            for y in range(image.nrows-1):
                image.set( (rho*R, y), 1 )
        for i in range(image.ncols-1):
            if rTheta > 0:
                yCoord = (rho / sin(rTheta)) - ( i * ( cos(rTheta) / sin(rTheta) ) )
                yCoord *= R
                if int(abs(yCoord)) < image.nrows-1:
                    image.set( (i, int(abs(yCoord))), 1 )

    image.save_PNG( r"%s"%output_image )

def calcMax(img, RT_c):
    """Searches for maxima in Hough-Space. When found, stores the pixelvalue and the x/y-coordinates."""
    max = []
    temp_max = (0.0,0,0)
    maxima = 0.0

    for x in range(5):
        for y in range(img.nrows):
            if maxima < img.get((x,y)):
                maxima = img.get((x, y))
                if maxima > RT_c:
                    temp_max = (maxima, x, y)
                    print temp_max
                    max.append(temp_max)

    maxima = 0.0

    for x in range(85,95):
        for y in range(img.nrows):
            if maxima < img.get((x, y)):
                maxima = img.get((x, y))
                if maxima > RT_c:
                    temp_max = (maxima,x,y)
                    print temp_max
                    max.append(temp_max)

    maxima = 0.0

    for x in range(175,180):
        for y in range(img.nrows):
            if maxima < img.get((x, y)):
                maxima = img.get((x, y))
                if maxima > RT_c:
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
    R = 0.2 * avg_height
    count = 0
    print "R = ", R
    print "Performing hough transformation..."
    args = []
    floatImage = tss.plugins.TextStringSep.hough_transform(ccs, args, [0.0,5.0,85.0,95.0,175.0,185.0],R,1.0,onebit0.ncols,onebit0.nrows)
    RT_c = 20

    #12
    while count != 1:
        #11
        while RT_c > 2:
            print "Calculate maximas..."
            max = calcMax(floatImage, RT_c)
            print "maximas: ", max

            #4
            for i in max:
                fclus = 5
                ftheta = i[1]
                theta = int(ftheta)
                rho = i[2]
#                print "cclist = ", args[0][theta][rho]

                #5
                cluster = []
                cluster.append(rho)
                for x in range(1,fclus):
                    if (x + rho) > int(R):
                        break
                    cluster.append(x+rho)

                for x in range(1,fclus):
                    if (x - rho) < 0:
                        break
                    cluster.append(x-rho)
                
                cluster_cc_pos_list = []
#                for n in cluster:
#                    cluster_cc_pos_list += args[0][theta][n]

                for n in cluster:
                    if n >= 0 and n <= (int(R) - 1):
                        for i in args[0][theta][n]:
                            if i not in cluster_cc_pos_list:
                                cluster_cc_pos_list.append(i)

                print "clustern: ", cluster_cc_pos_list

                #6
                cluster_cclist = []
                for i in cluster_cc_pos_list:
                    cluster_cclist.append(ccs[i])
                    
                H_a = calcAvgHeight(cluster_cclist)
                print "H_a = ", H_a

                #7 + 8
                fclus = int(H_a/R)
                print "fclus after re-clustering = ", fclus
                cluster = []
                cluster.append(rho)
                for x in range(1,fclus):
                    if (x + rho) > int(R):
                        break
                    cluster.append(x+rho)

                for x in range(1,fclus):
                    if (x - rho) < 0:
                        break
                    cluster.append(x-rho)

                #9 # 10
                # TODO

                #11
                RT_c -= 1

                #12
                # TODO


    floatImage.save_PNG(r"/home/olzzen/houghDomain.png")
 
    print "Draw found lines..."
    drawFoundLines(max, onebit0.ncols, onebit0.nrows, output_image, R)
    intx = 0
    inty = 0
    for x in args[0]:
#        print "type= ", type(args[0])
        intx += 1
#        print "laenge der ylist = ", len(x)
        for y in x:
            inty += 1
#            print "laenge der cclist = ", len(y)
            for cc in y:
#                print "position = ", cc
                text = "%i %i"%(intx,inty)
#                print "text = ", text
#                ccs[cc].draw_text( (1.0,1.0), text, 20 )
