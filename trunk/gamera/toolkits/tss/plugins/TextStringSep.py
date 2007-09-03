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
Stores values of the found maxima and the corresponding x-, y-coordinates.

img = FloatImage representing the hough-domain

RT_c = cell threshold

angelRange = intervals for theta (e.g. the x-axis in the hough-domain (0<= theta <= 180))"""
    max = []
    temp_max = (0.0,0,0)
    maxima = 0.0

    for theta in range(0,len(angleRange),2):
        if theta+1 >= len(angleRange):
            break

        startAngle = angleRange[theta]
        endAngle = angleRange[theta+1]

        for x in range(startAngle, endAngle):
            for y in range(img.nrows):
                if maxima <= img.get((x,y)):
                    maxima = img.get((x, y))
                    if maxima > RT_c:
                        temp_max = (maxima, x, y)
                        max.append(temp_max)

    return max

def calcAvgHeight(ccs):
    """Calculates the average height of a given set of CC's."""
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
    """Computes the difference between two values."""
    tmp = x[2] - y[2]
    if tmp == 0:
        return 0
    if tmp < 0:
        return int(floor(tmp))
    if tmp > 0:
        return int(ceil(tmp))

def string_segmentation(ccPositionList, cluster, ccs, string, groups, phrases, H_a, theta, R, orgY, twFact):
    """Inserts CC's depending on their height, the distance to their neighbors and
their orientation along the line into words and those words into phrases.

ccPositionList = contains the position of the CC in the original CC-List belonging to a theta/rho pair

cluster = contains rho values

ccs = original CC-List

string = CC's forming a cluster goes here

groups = CC's forming a word goes here

phrases = groups forming a phrase goes here

H_a = average height of CC's in the current string

theta = constant theta

R = rho-resolution in the hough-domain

hough_image = FloatImage representing the hough-domain"""
    gn = 0
    phrase = 0
    for g in range(100):
        groups.append(["i", None, None, 0])

    for i in cluster:
        if i >= 0 and i < orgY:
            for n in ccPositionList[0][theta][i]:
                if n not in string:
                    rho = abs((i - (orgY / 2)) * (-1) * R)
                    string.append([ccs[n], rho, None])

    # calculate distance along the line
    distance = 0
    distances = []
    for cc in string:
        hyp = abs(sqrt(pow(cc[0].center_y,2) + pow(cc[0].center_x,2)))
        distance = abs(sqrt(pow(hyp, 2) - pow(cc[1], 2)))
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
    
        tmp_length = len(tmp_strings)
        if tmp_length != 0:
            Hc /= tmp_length

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
    # TODO make "2.5" be a parameter so the user can choose a value
    if twFact <= 0.0:
        print "Negative value for twFact...set to 2.5"
        twFact = 2.5

    Tw = twFact * H_a

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
               groups[gn][2] = cc_i
            
            groups[gn][3] += 1 # increment character count

            if groups[gn][0] != 'p': # set group type to "word"
                groups[gn][0] = 'w'
        else:
            gn += 1 # select a new empty word group

            # now we know that character i does NOT belong to the same word group
            # so we finish the current word group and fill the phrase list
            if str[4] < Tw or str[4] == None: # De < Tw
                if len(phrases) == 0:
                    phrases.append([])
        
                phrases[-1].append(groups[gn-1])
                phrases[-1].append(groups[gn-2])

                #groups[gn][0] = 'p' # commented because testing
                groups[gn-1][0] = 'p'
                groups[gn-2][0] = 'p'
                gn += 1
            else:
                phrases.append([])

    for p in phrases:
        i = 0
        for g in p:
            if g[0] == 'i':
                i += 1
        if i > 2:
            print "too many initialized groups: I > 2"


class textStringSep(PluginFunction):
    """Separates text strings from mixed text/graphics images.

Returns the graphics part of the input-image.

rFact = Factor to compute the rho-resolution (e.g. rho-resolution = rFact * average-height)

t_precision = steps of theta in the hough domain

areaThres = argument is passed to area_ratio_filter_

xyThres = argument is passed to area_ratio_filter_
"""
    category = "Filter"
    self_type = ImageType([ONEBIT])
    return_type = ImageType([ONEBIT])
    args = Args([Float("rFact(a prior factor ;-) )"), Float("Steps for theta"), \
            Int("Average area threshold"), Int("Average height/width ratio threshold"), Float("Tw")])
    pure_python = 1 
    def __call__(self, rFact = 1.0, t_precision = 1.0, areaThres = 0, xyThres = 0, twFact = 2.5):
        print "Text/String separation started..."
        onebit = self.image_copy(DENSE)
        onebit.despeckle(8)
        ccs = onebit.area_ratio_filter(areaThres, xyThres)

        #1
        avg_height = calcAvgHeight(ccs)

        if rFact == 0.0:
            print "Senseless value for rFact...set to 1.0"
            rFact = 1.0 # should be "0.2", but "1.0" seems to be the better choice

        #2
        R = rFact * avg_height
        count = 0

        #3
        ccPositionList = []
        fImage = hough_transform(ccs, ccPositionList, [0.0 ,5.0 ,85.0 ,95.0 ,175.0 ,180.0], R, \
                                t_precision, onebit.ncols, onebit.nrows)
        RT_c = 20

        #12
        while count <= 1:
            #11
            while RT_c > 2:
                if count == 1:
                    max = calcMax(fImage, RT_c, [0.0, 180.0])
                else:
                    max = calcMax(fImage, RT_c, [0.0, 5.0, 85.0, 95.0, 175.0, 180.0])

                #4
                # iterate thru peaks in the hough-domain
                for i in max:
                    fclus = 5 # TODO make it a parameter to the user
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
                
                    # compute the correct average height of the CC's in the cluster
                    cluster_cc_pos_list = []
                    for n in cluster:
                        if n >= 0 and n <= (fImage.nrows):
                            for i in ccPositionList[0][theta][n]:
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

                    string_segmentation(ccPositionList, cluster, ccs, string, groups, phrases, \
                                        H_a, theta, int(R), fImage.nrows, twFact)

                    for p in phrases:
                        for g in p:
                            head = g[1]
                            num = g[3]

                            if head != None:
                                for cc_i in range(head, head+num+1):
                                    if cc_i < len(string):
                                        cc = string[cc_i][0]
                                        cc.fill_white()
                                        if cc in ccs:
                                            ccs.remove(cc)
                                        else:
                                            print "Step 9: error: CC-> ", cc, " <- is not in CC list"
                                    else:
                                        print "Step 9: error: OutOfBounds - CC(position) ->", cc_i, " <- does not exist"
                    
                    # free memory
                    del string
                    del phrases
                    del groups
                    del fImage
                    del ccPositionList

                    #10
                    ccPositionList = []
                    fImage = hough_transform(ccs, ccPositionList, [0.0, 5.0, 85.0, 95.0, 175.0, 180.0], \
                                R, t_precision, onebit.ncols, onebit.nrows)

                #11
                RT_c -= 1

            # free memory
            del fImage
            del ccPositionList
            
            count += 1
            if count == 1:
                ccPositionList = []
                RT_c = 20
                fImage = hough_transform(ccs, ccPositionList, [0.0, 5.0, 85.0, 95.0, 175.0, 180.0], R, t_precision, onebit.ncols, onebit.nrows)

        # DEBUG
        # fImage.save_PNG(r"~/houghDomain.png")
        
        return onebit
    __call__ = staticmethod(__call__)

class area_ratio_filter(PluginFunction):
    """Discard larger graphics in order to restrict processing to components
which are candidates for members of text strings.

Returns the connected components which are smaller or equal than the average area of CC's in the workingset.

If you don't know what effects those parameters have, leave them by default (e.g. "0").

areaThres = Average area-ratio threshold (will be used if unequal "0" otherwise the average area will be computed)

xyThres = Average width/height threshold (same as areaThres but it uses width/heigth ratio)
"""
    category = "Filter"
    selt_type = ImageType([ONEBIT])
    return_type = ImageList("ccs")
    pure_python = 1
    args=Args([Int("Average area-ratio threshold"), Int("Average width/height ratio threshold")])
    def __call__(self, areaThres = 0, xyThres = 0):
        print "Performing Area-Ratio filter..."
        ccs = self.cc_analysis()

        ccs_size = []
        for cc in ccs:
            if cc.ncols == 0 or cc.nrows == 0:
                print ""
            ccs_size.append((cc.nrows * cc.ncols, cc, cc.nrows / cc.ncols))
            
        ccs_size.sort()

        averageAreaRatio = 0
        if areaThres == 0:
            # calc arithmetical median of the area
            ccCount = len(ccs)
            for ccSize in ccs_size:
                averageAreaRatio += ccSize[0]
            if ccCount > 0:
                averageAreaRatio /= ccCount
        else:
            averageAreaRatio = areaThres

        # discard larger graphics depending on average area
        for ccSize in ccs_size:
            if ccSize[0] > (averageAreaRatio * 5):
                ccs.remove(ccSize[1])

        # discard CC's of which x/y-ratio is greater than -respectively-
        # equal to 20/1 or smaller than -respectively- equal to 1/20
        xyRatio = 0.0
        for ccSize in ccs_size:
            if ccSize[2] != 0:
                if xyThres == 0:
                    xyRatio = ccSize[2]
                else:
                    xyRatio = Float(xyThres)
                if xyRatio > 20.0 or xyRatio < 0.05:
                    ccs.remove(ccSize[1])
                xyRatio = 0.0

        return ccs
    __call__ = staticmethod(__call__)

class hough_transform(PluginFunction):
    """ Performs the Hough-Transformation for each centroid of an Image (e.g. CC) in the given ImageList.

imgVec = list of ccs

angleRange = list of angles (0.0<=theta<=180.0)

r = radius

t_precision = steps of theta (should not be changed from 1.0, because not implemented yet)

orgX = x size of original Image

orgY = y size of original Image
"""
    category = "Filter"
    self_type = None
    args = Args([ImageList("ccsImageList"), Class("resultList", list, False), FloatVector("angleRange"), \
                Float("r"), Float("t_precision"), Int("orgX"), Int("orgY")])
    return_type = ImageType([FLOAT])
    def __call__(ccsImageList, resultList, angleRange = array.array('f', [0.0, 180.0] ), \
                r = 1.0, t_precision = 1.0, orgX = 0, orgY = 0):
        return _TextStringSep.hough_transform(ccsImageList, resultList, angleRange, r, t_precision, orgX, orgY)
    __call__ = staticmethod(__call__)

class TextStringSepModule(PluginModule):
    """The holy logic ;-)"""
    category = "Tss"
    cpp_headers=["hough_transform.hpp"]
    cpp_namespace=["Gamera"]
    functions = [textStringSep,area_ratio_filter,hough_transform] 
    author = "Daniel Esser, Oliver Kriehn"
    url = "No URL"

module = TextStringSepModule()
hough_transform = hough_transform()
area_ratio_filter = area_ratio_filter()
