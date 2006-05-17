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
import _TextStringSep #import c++ side of the plugin

class textStringSep(PluginFunction):
    """Separates text strings from mixed text/graphics images"""
    category = "Filter"
    self_type = ImageType([ONEBIT])
    return_type = ImageType([ONEBIT])
    pure_python = 1 
    def __call__(self):
        H_ws = average height

        R = 0.2 * H_ws

    
        return null
    __call__ = staticmethod(__call__)


class area_ratio_filter(PluginFunction):
    """Discard larger graphics in order to restrict processing to components which are candidates for members of text strings"""
    category = "Filter"
    selt_type = ImageType([ONEBIT])
    return_type = ImageList("ccs")
    pure_python = 1
    def __call__(self):
        print(" - Starting Area/Ratio-Filter")

        print " |--CC Analysis"
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

       

        print avg_area
        print "erstes Element: ", ccs_size[0]
        print "letztes Element: ", ccs_size[ len(ccs_size)-1 ]
        

        return ccs
    __call__ = staticmethod(__call__)


class col_comp_grouping(PluginFunction):
    """ Beschreibung """
    category = "Filter"
    self_type = ImageList("ccs")
    return_type = ImageList("ccs")
    pure_python = 1
    def __call__(self):
        return null
    __call__ = staticmethod(__call__)


class hough_transform(PluginFunction):
    """ Performs the Hough-Transformation for each given point"""
    category = "Filter"
    self_type = ImageList("ccsImageList")
# hier sollte eigentlich ein PointVector an die Funktion uebergeben werden
# dieser wird dann durchgearbeitet, und ein entsprechender PointVector wird geliefert
#    args = Args([PointVector("ccsPointVector")])
    return_type = Class("ht",tuple,True)

class TextStringSepModule(PluginModule):
    category = "Tss"
    cpp_headers=["hough_transform.hpp"]
    cpp_namespace=["Gamera"]
    functions = [textStringSep,col_comp_grouping,area_ratio_filter,hough_transform] 
    author = "Your name here"
    url = "Your URL here"

module = TextStringSepModule()
#col_comp_grouping = col_comp_grouping()
#hough_transform = hough_transform()
area_ratio_filter = area_ratio_filter()
