#   $Id: TextStringSep.py 7 2006-04-20 19:49:14Z desser $
#   Copyright (C) 2006  Daniel Esser, Oliver Kriehn
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
from gamera.plugin import *
import gamera.core
from gamera import *
from cmath import *
from math import *
import _TextStringSep #import c++ side of the plugin
import array

def calcMax(img, RT_c, angleRange):
    """Detects the maxima in the hough-domain. Stores values of the found maximas and the corresponding x-, y-Coords."""
    max = []
    temp_max = (0.0,0,0)
    maxima = 0.0

    for theta in range(len(angleRange)-1):
        if theta+1 >= len(angleRange):
            break
        startAngle = angleRange[theta]
        endAngle = angleRange[theta+1]
        #print "starting at: ", startAngle, "ending at: ", endAngle
        for x in range(startAngle,endAngle):
            for y in range(img.nrows):
                if maxima <= img.get((x,y)):
                    maxima = img.get((x, y))
                    if maxima > RT_c:
                        temp_max = (maxima, x, y)
                        max.append(temp_max)
        theta += 1

    return max

def calcAvgHeight(ccs):
    """Simple function to calculate the average height of a given set of ccs."""
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
    """Simple function to compare two values."""
    tmp = x[2] - y[2]
    if tmp == 0:
        return 0
    if tmp < 0:
        return int(floor(tmp))
    if tmp > 0:
        return int(ceil(tmp))

'''
class string_segmentation(PluginFunction):
    """Separates text from mixed text/graphics images"""
    category = "Filter"
    self_type = None
    return_type = None
    args =  Args( [Class("resultList", list, False), IntVector("cluster"), ImageList("ccs"), Class("stringlist", list, False), Class("grouplist", list, False), Class("phraselist", list, False), Int("H_a"), Int("theta"), Int("R"), Class("houghdomain", list, False)] )
    #pure_python = 1
    def __call__(resultList, cluster, ccs, string, groups, phrases, H_a, theta, R, hough_image):
        print "Calling text_extract()"
        
        gn = 0
        phrase = 0
        for g in range(100):
            groups.append( ["i", None, None, 0] )

        for i in cluster:
            if i >= 0 and i < hough_image.nrows:
                for n in resultList[0][theta][i]:
                    if n not in string:
                        rho = abs((i - (hough_image.nrows / 2)) * (-1) * R)
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
        for cc_i in range(len(string)):
            offset = 0
            tmp_strings = [string[cc_i]]
            i = 4

            while i > 0:
                offset += 1
                new_cc = cc_i + offset

                if new_cc >= 0 and new_cc < len(string):
                    i -= 1
                    tmp_strings.append(string[new_cc])

                offset *= -1
                new_cc = cc_i + offset
                if new_cc >= 0 and new_cc < len(string) and i > 0:
                    i -= 1
                    tmp_strings.append(string[new_cc])

            # calculate Hc
            Hc = 0
            for str in tmp_strings:
                Hc += str[0].nrows
            Hc /= len(tmp_strings)

            string[cc_i].append(Hc)

        # calculate De
        for cc_i in range(len(string)):
            next_cc = cc_i + 1
            if next_cc >= 0 and next_cc < len(string):
                De = string[cc_i][0].distance_bb(string[next_cc][0])
                string[cc_i].append(De)
            else:
                string[cc_i].append(None)

        # calculate the inter word gap threshold
        Tw = 2.5 * H_a

        # search for words and phrases
        for cc_i in range(len(string)):
            str = string[cc_i]

            #print str[4]

            # check edge to edge distance against the local inter character gap threshold
            if str[4] != None and str[4] <= str[3]: # D_e <= T_c

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

                # now we know that character i does NOT belong to the same sentence
                # so we finish the current word group and fill the phrase list
                if str[4] < Tw or str[4] == None: # De < Tw

                    if len(phrases) == 0:
                        phrases.append([])
                    phrases[-1].append( groups[gn-1] )
#                   phrases[-1].append( groups[gn] )
#                   groups[gn][0] = 'p' #Zum Test auskommentiert
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

    __call__ = staticmethod(__call__)'''

def string_segmentation(args, cluster, ccs, string, groups, phrases, H_a, theta, R, houghY):
    """Separates text from mixed text/graphics images"""
    print "Performing string_segmentation..."
    gn = 0
    phrase = 0
    for g in range(100):
        groups.append( ["i", None, None, 0] )

    for i in cluster:
        if i >= 0 and i < hough_image.nrows:
            for n in args[0][theta][i]:
                if n not in string:
                    rho = abs((i - (houghY / 2)) * (-1) * R)
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
    for cc_i in range(len(string)):
        offset = 0
        tmp_strings = [string[cc_i]]
        i = 4

        while i > 0:
            offset += 1
            new_cc = cc_i + offset

            if new_cc >= 0 and new_cc < len(string):
                i -= 1
                tmp_strings.append(string[new_cc])

            offset *= -1
            new_cc = cc_i + offset
            if new_cc >= 0 and new_cc < len(string) and i > 0:
                i -= 1
                tmp_strings.append(string[new_cc])

        # calculate Hc
        Hc = 0
        for str in tmp_strings:
            Hc += str[0].nrows
        if len(tmp_strings) != 0:
            Hc /= len(tmp_strings)

        string[cc_i].append(Hc)

    # calculate De
    for cc_i in range(len(string)):
        next_cc = cc_i + 1
        if next_cc >= 0 and next_cc < len(string):
            De = string[cc_i][0].distance_bb(string[next_cc][0])
            string[cc_i].append(De)
        else:
            string[cc_i].append(None)

    # calculate the inter word gap threshold
    Tw = 2.5 * H_a

    # search for words and phrases
    for cc_i in range(len(string)):
        str = string[cc_i]

        #print str[4]

        # check edge to edge distance against the local inter character gap threshold
        if str[4] != None and str[4] <= str[3]: # D_e <= T_c

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

            # now we know that character i does NOT belong to the same sentence
            # so we finish the current word group and fill the phrase list
            if str[4] < Tw or str[4] == None: # De < Tw

                if len(phrases) == 0:
                    phrases.append([])
                phrases[-1].append( groups[gn-1] )
#               phrases[-1].append( groups[gn] )
#               groups[gn][0] = 'p' #Zum Test auskommentiert
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

class textStringSep(PluginFunction):
    """Separates text strings from mixed text/graphics images. Returns the graphics part of the input-image."""
    category = "Filter"
    self_type = ImageType([ONEBIT])
    return_type = ImageType([ONEBIT])
    args = Args([Float("rFakt")])
    pure_python = 1 
    def __call__(self, rFakt = 0.5):
        print "Text/String separation started..."
        onebit0 = self
        ccs = self.area_ratio_filter()
        avg_height = calcAvgHeight(ccs)
        R = floor(rFakt * avg_height)
        count = 0
        args = []
        floatImage = hough_transform(ccs, args, [0.0,5.0,85.0,95.0,175.0,180.0],R,1.0,self.ncols, self.nrows)
        
        RT_c = 20
        #12
        while count <= 1:
            #11
            while RT_c > 2:
                #print "--------------------------------- ", RT_c
                max = calcMax(floatImage, RT_c, [0,5,85,95,175,180])
                #if len(max) != 0:
                    #print "found maximas: ", max

                #4
                # iterate thru peaks in the hough-domain
                for i in max:
                    fclus = 5
                    ftheta = i[1]
                    theta = int(ftheta)
                    rho = i[2]
                    #print "CCs der Maximas: ", args[0][theta][rho]

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

                    #print "Cluster ", cluster
                
                    # only needed to compute the correct average height of the cc's in the working set
                    cluster_cc_pos_list = []
                    for n in cluster:
                        if n >= 0 and n <= (floatImage.nrows):
                            for i in args[0][theta][n]:
                                if i not in cluster_cc_pos_list:
                                    cluster_cc_pos_list.append(i)

                    #print "clustern: ", cluster_cc_pos_list

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

                    #print "Reclustering with ", fclus

                    for x in range(1,fclus):
                        if (x + rho) > floatImage.nrows:
                            break
                        cluster.append(x+rho)

                    for x in range(1,fclus):
                        if (x - rho) < 0:
                            break
                        cluster.append(x-rho)

                    #print "Recluster ", cluster

                    #9
                    # Reset our information lists
                    string = []
                    groups = []
                    phrases = []
                    string_segmentation(args, cluster, ccs, string, groups, phrases, H_a, theta, int(R), floatImage.nrows)

                    for p in phrases:
                        for g in p:
                            head = g[1]
                            num = g[3]

                            if head != None:
                                #rand_color = gamera.core.RGBPixel( randrange(0,255), randrange(0,255), randrange(0,255) )

                                for cc_i in range(head, head+num+1):

                                    if cc_i < len(string):
                                        cc = string[cc_i][0]
                                        #print cc
                                        #image0.highlight(cc, gamera.core.RGBPixel(200,200,200) )
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

                    string = None
                    phrases = None
                    groups = None

                    #print "After String Segmentation ", len(ccs), " connected components remaining"

                    #10

                    del floatImage
                    del args

                    args = []
                    floatImage = hough_transform(ccs, args, [0.0,5.0,85.0,95.0,175.0,180.0],R,1.0,onebit0.ncols,onebit0.nrows)

                #11
                RT_c -= 1

            count += 1
            if count == 1:
                args = []
                RT_c = 20
                floatImage = hough_transform(ccs, args, [0.0,180.0],R,1.0,onebit0.ncols,onebit0.nrows)
                floatImage.save_PNG(r"float.png")

        # DEBUG
#       floatImage.save_PNG(r"houghDomain.png")
#       image0.save_PNG(r"out2.png")
        onebit0.save_PNG(r"grafik.png")
        
        return onebit0
    __call__ = staticmethod(__call__)


class area_ratio_filter(PluginFunction):
    """Discard larger graphics in order to restrict processing to components which are candidates for members of text strings. Returns the connected components which are smaller or equal than the average height."""
    category = "Filter"
    selt_type = ImageType([ONEBIT])
    return_type = ImageList("ccs")
    pure_python = 1
    def __call__(self):
        print "Performing area_ratio_filter..."
        ccs = self.cc_analysis()

        ccs_size = []
        for i in ccs:
            ccs_size.append( (i.nrows * i.ncols, i)  )
            
        ccs_size.sort()

        # calc arithmetical median of the area
        length = len(ccs)
        avg_area = 0
        for i in ccs_size:
            avg_area += i[0]
        avg_area /= length
        #print "Average Area: ", avg_area

        # discard larger graphics depending on average area
        for cct in ccs_size:
            if cct[0] > (avg_area*5):
                ccs.remove(cct[1])

        '''for cc in ccs:
            if cc.ncols != 0 and cc.nrows != 0:
                ratio = cc.ncols / cc.nrows
                if ratio >= 20 or ratio <= 0.05:
                    ccs.remove(cc)'''

        return ccs
    __call__ = staticmethod(__call__)

class hough_transform(PluginFunction):
    """ Performs the Hough-Transformation for each centroid of an Image in the given ImageList\nhough_transform( ImageVector &imgVec, IntVector *angleRange, int r, float t_precision, int orgX, int orgY )\nimgVec = list of ccs\nangleRange = list of angles ( 0.0 <= theta <= 1.0\nr = radius\nt_precision = steps of theta (should not be changed from 1.0, because not implemented yet)\norgX = x size of original Image\norgY = y size of original Image"""
    category = "Filter"
    self_type = None
    args = Args( [ImageList("ccsImageList"), Class("resultList", list, False), FloatVector("angleRange"), Float("r"), Float("t_precision"), Int("orgX"), Int("orgY")] )
    return_type = ImageType([FLOAT])
    def __call__( ccsImageList, resultList, angleRange = array.array('f', [0.0, 180.0] ), r = 1.0, t_precision = 1.0, orgX = 0, orgY = 0 ):
        print "Performing hough_transform..."
        return _TextStringSep.hough_transform(ccsImageList, resultList, angleRange, r, t_precision, orgX, orgY)
    __call__ = staticmethod(__call__)

class TextStringSepModule(PluginModule):
    category = "Tss"
    cpp_headers=["hough_transform.hpp"]
    cpp_namespace=["Gamera"]
    functions = [textStringSep,area_ratio_filter,hough_transform] 
    author = "Daniel Esser, Oliver Kriehn"
    url = "Your URL here"

module = TextStringSepModule()
hough_transform = hough_transform()
area_ratio_filter = area_ratio_filter()
