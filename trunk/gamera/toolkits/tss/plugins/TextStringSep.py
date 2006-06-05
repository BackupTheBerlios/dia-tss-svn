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
from gamera import *
from cmath import *
import _TextStringSep #import c++ side of the plugin
import array

def drawFoundLines(max, width, height, image):
    """Draws the lines depending on theta and rho."""
    for x in max:
        pixelValue = x[0]
        theta = x[1]
        rho = x[2]
        rTheta = (theta * pi) / 180.0
        for i in range(image.ncols-1):
            yCoord = (rho / sin(rTheta)) - ( i * ( cos(rTheta) / sin(rTheta) ) )
            if int(abs(yCoord)) < image.ncols-1:
                image.set((i, int(abs(yCoord))), 100 )

    image.display()

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

class textStringSep(PluginFunction):
    """Separates text strings from mixed text/graphics images"""
    category = "Filter"
    self_type = ImageType([ONEBIT])
    return_type = ImageType([ONEBIT])
    pure_python = 1 
    def __call__(self):
#        H_ws = average height

#        R = 0.2 * H_ws
    
        return null
    __call__ = staticmethod(__call__)


class area_ratio_filter(PluginFunction):
    """Discard larger graphics in order to restrict processing to components which are candidates for members of text strings"""
    category = "Filter"
    selt_type = ImageType([ONEBIT])
    return_type = ImageList("ccs")
    pure_python = 1
    def __call__(self):
        print("- Starting Area/Ratio-Filter")

        print "|-CC Analysis"
        '''Connected Component Analysis'''
        ccs = self.cc_analysis()

        ccs_size = []
        for i in ccs:
            ccs_size.append( (i.nrows * i.ncols, i)  )
            
        ccs_size.sort() # Wie wird hier sortiert?

        '''calc arithmetical median of the area'''
        length = len(ccs)        
        avg_area = 0        
        for i in ccs_size:
            avg_area += i[0]
        
        avg_area /= length

        '''discard larger graphics'''
        for cct in ccs_size:
            if cct[0] > (avg_area*5):
                cct[1].fill_white()

        '''calc histogram'''
#        max_distance = 
#        max_ratio

 
#        if (length % 2) == 0:
#            avg_area = length / 2
#        else:
#            avg_area = (length+1) / 2

        print "Average Area: ", avg_area

        print "|--Hough Transformation"
        '''Perform Hough Transformation'''
        testFloatImage = hough_transform( ccs, [0.0,5.0,85.0,95.0,175.0,180.0], 1, 0.3, self.ncols, self.nrows )
        
        print "|---calulate maxima"
        '''calc maxima in hough-space'''
        max = calcMax( testFloatImage )
        print "maxima (pixelvalue, theta, rho):\n", max

        testFloatImage.display()

        return ccs
    __call__ = staticmethod(__call__)


class col_comp_grouping(PluginFunction):
    """ Beschreibung """
    category = "Filter"
    self_type = ImageList("ccs")
    return_type = ImageList("ccs")
    pure_python = 1
    def __call__(self):
        return None
    __call__ = staticmethod(__call__)


class hough_transform(PluginFunction):
    """ Performs the Hough-Transformation for each centroid of an Image in the given ImageList\nhough_transform( ImageVector &imgVec, FloatVector *angleRange, int r, float t_precision, int orgX, int orgY )\nimgVec = list of ccs\nangleRange = list of angles ( 0.0 <= theta <= 1.0\nr = radius\nt_precision = steps of theta\norgX = x size of original Image\norgY = y size of original Image"""
    category = "Filter"
    self_type = None
    args = Args( [ImageList("ccsImageList"), FloatVector("angleRange"), Int("r"), Float("t_precision"), Int("orgX"), Int("orgY")] )
    return_type = ImageType( [FLOAT] )
    def __call__( ccsImageList, angleRange = array.array( 'f', [0.0, 360.0] ), r = 1, t_precision = 1.0, orgX = 0, orgY = 0 ):
        return _TextStringSep.hough_transform(ccsImageList, angleRange, r, t_precision, orgX, orgY)
    __call__ = staticmethod(__call__)

class TextStringSepModule(PluginModule):
    category = "Tss"
    cpp_headers=["hough_transform.hpp"]
    cpp_namespace=["Gamera"]
    functions = [textStringSep,col_comp_grouping,area_ratio_filter,hough_transform] 
    author = "Daniel Esser, Oliver Kriehn"
    url = "Your URL here"

module = TextStringSepModule()
#col_comp_grouping = col_comp_grouping()
hough_transform = hough_transform()
area_ratio_filter = area_ratio_filter()
