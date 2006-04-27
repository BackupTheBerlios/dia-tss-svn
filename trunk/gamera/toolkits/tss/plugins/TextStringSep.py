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

class textStringSep(PluginFunction):
    """Separates text strings from mixed text/graphics images"""
    category = "Filter"
    self_type = ImageType([ONEBIT])
    return_type = ImageType([ONEBIT])
    pure_python = 1 
    def __call__(self):
        return null
    __call__ = staticmethod(__call__)


class area_ratio_filter(PluginFunction):
    """Discard larger graphics in order to restrict processing to components which are candidates for members of text strings"""
    category = "Filter"
    return_type = ImageList("ccssmall")
    args = Args( [ImageList("ccs")] )
    pure_python = 1
    def __call__(self, ccs):
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
    """ Beschreibung """
    category = "Filter"
    self_type = ImageList("ccs")
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
