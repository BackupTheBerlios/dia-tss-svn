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
from math import *
from random import *
from time import *
import gc
import pdb
import os

def calcMax(img, RT_c, angleRange):
    """Detects the maxima in the hough-domain. Stores values of the found maximas and the corresponding x-, y-Coords."""
    max = []
    temp_max = (0.0,0,0)
    maxima = 0.0

    for theta in range(0,len(angleRange),2):
        if theta+1 >= len(angleRange):
            break

        startAngle = angleRange[theta]
        endAngle = angleRange[theta+1]

        for x in range(startAngle,endAngle):
            for y in range(img.nrows):
                if maxima <= img.get((x,y)):
                    maxima = img.get((x, y))
                    if maxima > RT_c:
                        temp_max = (maxima, x, y)
                        max.append(temp_max)

    return max

def calcAvgHeight(ccs):
    """Simple function to calculate the average height of a given set of CC's."""
    avg_height = 0
    
    for i in ccs:
        avg_height += i.nrows

    cc_count = len(ccs)
    if cc_count != 0:
        for i in ccs:
            avg_height += i.nrows
        avg_height /= cc_count

    return avg_height

def compare(x, y):
    """Simple function to compute the difference between two values."""
    tmp = x[2] - y[2]
    if tmp == 0:
        return 0
    if tmp < 0:
        return int(floor(tmp))
    if tmp > 0:
        return int(ceil(tmp))


def string_segmentation(args, cluster, ccs, string, groups, phrases, H_a, theta, R, hough_image):
    """Inserts CC's depending on their height, the distance to their neighbors and their orientation along the line into words and those words into phrases."""
# args contains the position of a cc in the ccs-list belonging to a theta/rho pair
# cluster contains rho-values building a cluster
    gn = 0
    phrase = 0
    for g in range(100):
        groups.append( ["i", None, None, 0] )

    orgY = hough_image.nrows
    for i in cluster:
        if i >= 0 and i < orgY:
            for n in args[0][theta][i]:
                if n not in string:
                    rho = abs((i - (orgY / 2)) * (-1) * R)
                    string.append( [ccs[n], rho, None] )

    # calculate distance along the line
    distance = 0
    distances = []
    for cc in string:
        hyp = abs(sqrt( pow(cc[0].center_y,2) + pow(cc[0].center_x,2) ))
        distance = abs(sqrt( pow(hyp, 2) - pow(cc[1], 2) ))
        cc[2] = distance

    # sort ccs corresponding to their distance along the line
    string.sort(cmp=compare)

    # form cluster
    strlength = len(string)
    for cc_i in range(strlength):
        offset = 0
        tmp_strings = [string[cc_i]]
        i = 4

        while i > 0:
            offset += 1
            new_cc_i = cc_i + offset

            if new_cc_i >= 0 and new_cc_i < strlength:
                i -= 1
                tmp_strings.append(string[new_cc_i])

            offset *= -1
            new_cc_i = cc_i + offset
            if new_cc_i >= 0 and new_cc_i < strlength and i > 0:
                i -= 1
                tmp_strings.append(string[new_cc_i])

        # calculate Hc
        Hc = 0
        for str in tmp_strings:
            Hc += str[0].nrows
        Hc /= len(tmp_strings)

        string[cc_i].append(Hc)

    # calculate De
    strlength = len(string)
    for cc_i in range(strlength):
        next_cc_i = cc_i + 1
        if next_cc_i >= 0 and next_cc_i < strlength:
            De = string[cc_i][0].distance_bb(string[next_cc_i][0])
            string[cc_i].append(De)
        else:
            string[cc_i].append(None)

    # calculate the inter word gap threshold
    Tw = 2.5 * H_a

    # search for words and phrases
    strlength = len(string)
    for cc_i in range(strlength):
        str = string[cc_i]

        # check edge to edge distance against the local inter character gap threshold
        if str[4] != None and str[4] <= str[3]: # De <= Tc

            # now we know that character i and i+1 belongs to the same word group
            # so we add it to the same word group
            if groups[gn][0] == 'i':
               groups[gn][1] = cc_i
               groups[gn][2] = cc_i + 1
            else:
               groups[gn][2] = cc_i + 1
            
            groups[gn][3] += 1 # increment character count

            if groups[gn][0] != 'p': # set group type to "word"
                groups[gn][0] = 'w'
        else:
            gn += 1 # select a new empty word group

            # now we know that character i does NOT belong to a word within the same phrase
            # so we finish the current word group and fill the phrase list
            if str[4] < Tw or str[4] == None: # De < Tw
                if len(phrases) == 0:
                    phrases.append([])
                phrases[-1].append( groups[gn-1] )
#                phrases[-1].append( groups[gn] )
#                groups[gn][0] = 'p' # commented because testing
                groups[gn-1][0] = 'p'
            else:
                phrases.append([])

    for p in phrases:
        i = 0
        for g in p:
            if g[0] == 'i':
                i += 1
        if i > 2:
            print "Zuviele I's"

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

    if image0.pixel_type_name != "OneBit":
        onebit0 = image0.to_onebit()
    else:
        onebit0 = image0

    onebit0.despeckle(8)

    ccs = onebit0.area_ratio_filter()
    avg_height = calcAvgHeight(ccs)
    R = 0.5 * avg_height
    count = 0

    args = []
    floatImage = tss.plugins.TextStringSep.hough_transform(ccs, args, [0.0,5.0,85.0,95.0,175.0,180.0],R,1.0,onebit0.ncols,onebit0.nrows)

    RT_c = 20
    #12
    while count <= 1:
        #11
        while RT_c > 2:
            if count == 1:
                max = calcMax(floatImage, RT_c, [0,180])
            else:
                max = calcMax(floatImage, RT_c, [0,5,85,95,175,180])

            #4
            # iterate thru peaks in the hough-domain
            for i in max:
                fclus = 5
                ftheta = i[1]
                theta = int(ftheta)
                rho = i[2]

                #5
                # form cluster
                cluster = []
                cluster.append(rho)
                for x in range(1,fclus):
                    if (x + rho) > floatImage.nrows:
                        break
                    cluster.append(x+rho)

                for x in range(1,fclus):
                    if (x - rho) < 0:
                        break
                    cluster.append(x-rho)
                
                # only needed to compute the correct average height of the cc's in the working set
                cluster_cc_pos_list = []
                for n in cluster:
                    if n >= 0 and n <= (floatImage.nrows):
                        for i in args[0][theta][n]:
                            if i not in cluster_cc_pos_list:
                                cluster_cc_pos_list.append(i)

                cluster_cclist = []
                for i in cluster_cc_pos_list:
                    cluster_cclist.append(ccs[i])

                #6
                H_a = calcAvgHeight(cluster_cclist)

                #7 + 8
                # re-clustering
                fclus = int(H_a/R)
                cluster = []
                cluster.append(rho)

                for x in range(1,fclus):
                    if (x + rho) > floatImage.nrows:
                        break
                    cluster.append(x+rho)

                for x in range(1,fclus):
                    if (x - rho) < 0:
                        break
                    cluster.append(x-rho)

                #9
                # Reset our information lists
                string = []
                groups = []
                phrases = []
                string_segmentation(args, cluster, ccs, string, groups, phrases, H_a, theta, int(R), floatImage)

                for p in phrases:
                    for g in p:
                        head = g[1]
                        num = g[3]

                        if head != None:
                            rand_color = RGBPixel( randrange(0,255), randrange(0,255), randrange(0,255) )

                            for cc_i in range(head, head+num+1):
                                if cc_i < len(string):
                                    cc = string[cc_i][0]
                                    #print cc
                                    image0.highlight(cc, RGBPixel(200,200,200) )
                                    #image0.highlight(cc, rand_color)
                                    cc.fill_white()
                                    if cc in ccs:
                                        ccs.remove(cc)
                                    else:
                                        print "Step 9: CC ", cc, " is not in CC list"
                                else:
                                    print "Step 9: OutOfBounds-Error - CC ", cc_i, " does not exist"
                    
                # free memory
                del string
                del phrases
                del groups
                del floatImage
                del args

                #10
                args = []
                floatImage = tss.plugins.TextStringSep.hough_transform(ccs, args, [0.0,5.0,85.0,95.0,175.0,180.0],R,1.0,onebit0.ncols,onebit0.nrows)

            #11
            RT_c -= 1

        count += 1
        if count == 1:
            args = []
            RT_c = 20
            floatImage = tss.plugins.TextStringSep.hough_transform(ccs, args, [0.0,180.0],R,1.0,onebit0.ncols,onebit0.nrows)
            floatImage.save_PNG(r"float.png")

    #12
    # DEBUG
#    floatImage.save_PNG(r"houghDomain.png")
    image0.save_PNG(r"out2.png")
    onebit0.save_PNG(r"grafik.png")
