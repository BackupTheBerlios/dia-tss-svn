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
    self_type = ImageList("ccs")
    return_type = ImageList("ccs")
    pure_python = 1

    def __call__(self):
        return null

    __call__ = staticmethod(__call__)


class TextStringSepModule(PluginModule):
    category = "Dia-tss"
    '''cpp_headers=["TextStringSep.hpp"]'''
    '''cpp_namespace=["Gamera"]'''
    functions = [textStringSep,area_ratio_filter]
    author = "Your name here"
    url = "Your URL here"

module = TextStringSepModule()
textStringSep = textStringSep()
