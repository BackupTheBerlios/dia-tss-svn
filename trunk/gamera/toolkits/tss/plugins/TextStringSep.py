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
    """Detects the maxima in the hough-domain.
Stores values of the found maximas and the corresponding x-, y-Coords."""
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
    """Inserts CC's depending on their height, the distance to their neighbors and
their orientation along the line into words and those words into phrases."""
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
            print "too many ititialized groups: I > 2"


class textStringSep(PluginFunction):
    """Separates text strings from mixed text/graphics images.

Returns the graphics part of the input-image.

rFactor = Factor to compute the rho-resolution (e.g. rho-resolution = rFactor * average-height)

aThres = see area_ratio_filter_

hThres = see area_ratio_filter_
"""
    category = "Filter"
    self_type = ImageType([ONEBIT])
    return_type = ImageType([ONEBIT])
    args = Args([Float("rFactor"), Int("Average area threshold"),\
                Int("Average height/width ratio threshold")])
    pure_python = 1 
    def __call__(self, rFact = 0.5, aThres = 0, hThres = 0):
        print "Text/String separation started..."
        onebit = self.image_copy(DENSE)
        onebit.despeckle(8)
        ccs = onebit.area_ratio_filter(aThres, hThres)
        avg_height = calcAvgHeight(ccs)
        
        if rFact == 0.0:
            rFact = 0.5

        R = rFact * avg_height
        args = []
        fImage = hough_transform(ccs, args, [0.0,5.0,85.0,95.0,175.0,180.0], R,\
                                1.0, onebit.ncols, onebit.nrows)
        
        count = 0
        RT_c = 20
        #12
        while count <= 1:
            print "Hough-Transformation and String Segmentation..."
            #11
            while RT_c > 2:
                if count == 1:
                    max = calcMax(fImage, RT_c, [0,180])
                else:
                    max = calcMax(fImage, RT_c, [0,5,85,95,175,180])
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
                        if (x + rho) > fImage.nrows:
                            break
                        cluster.append(x+rho)

                    for x in range(1,fclus):
                        if (x - rho) < 0:
                            break
                        cluster.append(x-rho)
                
                    # only needed to compute the correct average height of the cc's in the working set
                    cluster_cc_pos_list = []
                    for n in cluster:
                        if n >= 0 and n <= (fImage.nrows):
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
                        if (x + rho) > fImage.nrows:
                            break
                        cluster.append(x+rho)

                    for x in range(1,fclus):
                        if (x - rho) < 0:
                            break
                        cluster.append(x-rho)

                    #9
                    string = []
                    groups = []
                    phrases = []
                    string_segmentation(args, cluster, ccs, string, groups, phrases,\
                                        H_a, theta, int(R), fImage)

                    for p in phrases:
                        for g in p:
                            head = g[1]
                            num = g[3]

                            if head != None:
                                rand_color = gamera.core.RGBPixel( 250, 250, 250 )

                                for cc_i in range(head, head+num+1):
                                    if cc_i < len(string):
                                        cc = string[cc_i][0]
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
                    del fImage
                    del args

                    #10
                    args = []
                    fImage = hough_transform(ccs, args, [0.0,5.0,85.0,95.0,175.0,180.0],R,\
                                            1.0,onebit.ncols,onebit.nrows)

                #11
                RT_c -= 1

            # free memory
            del fImage
            del args
            
            count += 1
            if count == 1:
                args = []
                RT_c = 20
                fImage = hough_transform(ccs, args, [0.0,180.0],R,1.0,onebit.ncols,onebit.nrows)
                fImage.save_PNG(r"float.png")

        # DEBUG
#        fImage.save_PNG(r"houghDomain.png")
#        onebit.save_PNG(r"grafik.png")
        
        return onebit
    __call__ = staticmethod(__call__)

class area_ratio_filter(PluginFunction):
    """Discard larger graphics in order to restrict processing to components
which are candidates for members of text strings.

Returns the connected components which are smaller or equal than the average area of CC's in the workingset.

If you don't know what effects that parameters have leave them by default.

aThres = Average area-ratio threshold (will be used if unequal 0 otherwise the average area will be computed)

hThres = Average heigh/width threshold (same as aThres but it uses height/width ratio)
"""
    category = "Filter"
    selt_type = ImageType([ONEBIT])
    return_type = ImageList("ccs")
    pure_python = 1
    args=Args([Int("Average area-ratio threshold"), Int("Average height/width ratio threshold")])
    def __call__(self, aThres = 0, hThres = 0):
        print "Performing Average-Area-Filter..."
        ccs = self.cc_analysis()

        ccs_size = []
        for i in ccs:
            if i.ncols != 0:
                ccs_size.append( (i.nrows * i.ncols, i, i.nrows / i.ncols)  )
            
        ccs_size.sort()

        avg_area = 0
        if aThres == 0:
            # calc arithmetical median of the area
            length = len(ccs)
            avg_area = 0
            for i in ccs_size:
                avg_area += i[0]
            avg_area /= length
        else:
            avg_area = aThres

        # discard larger graphics depending on average area
        for cct in ccs_size:
            if cct[0] > (avg_area*5):
                ccs.remove(cct[1])

        # discard CC's of which x/y-ratio is greater than -respectively-
        # equal to 20/1 or smaller than -respectively- equal to 1/20
        ratio = 0.0
        for cc in ccs_size:
            if cc[2] != 0:
                if hThres == 0:
                    ratio = cc[2]
                else:
                    ratio = Float(hThres)
                if ratio > 20.0 or ratio < 0.05:
                    ccs.remove(cc[1])
                ratio = 0.0

        return ccs
    __call__ = staticmethod(__call__)

class hough_transform(PluginFunction):
    """ Performs the Hough-Transformation for each centroid of an Image (e.g. CC) in the given ImageList.

hough_transform( ImageVector &imgVec, IntVector *angleRange, int r, float t_precision, int orgX, int orgY )

imgVec = list of ccs

angleRange = list of angles ( 0.0 <= theta <= 1.0

r = radius

t_precision = steps of theta (should not be changed from 1.0, because not implemented yet)

orgX = x size of original Image

orgY = y size of original Image
"""
    category = "Filter"
    self_type = None
    args = Args([ImageList("ccsImageList"), Class("resultList", list, False), FloatVector("angleRange"),\
                Float("r"), Float("t_precision"), Int("orgX"), Int("orgY")])
    return_type = ImageType([FLOAT])
    def __call__(ccsImageList, resultList, angleRange = array.array('f', [0.0, 180.0] ),\
                r = 1.0, t_precision = 1.0, orgX = 0, orgY = 0):
        return _TextStringSep.hough_transform(ccsImageList, resultList, angleRange, r, t_precision, orgX, orgY)
    __call__ = staticmethod(__call__)

class TextStringSepModule(PluginModule):
    category = "Tss"
    cpp_headers=["hough_transform.hpp"]
    cpp_namespace=["Gamera"]
    functions = [textStringSep,area_ratio_filter,hough_transform] 
    author = "Daniel Esser, Oliver Kriehn"
    url = "No URL"

module = TextStringSepModule()
hough_transform = hough_transform()
area_ratio_filter = area_ratio_filter()
