"""
Toolkit setup

This file is run on importing anything within this directory.
Its purpose is only to help with the Gamera GUI shell,
and may be omitted if you are not concerned with that.
"""

from gamera import toolkit
from wxPython.wx import *
from gamera.toolkits.dia-tss import main

# Let's import all our plugins here so that when this toolkit
# is imported using the "Toolkit" menu in the Gamera GUI
# everything works.

from gamera.toolkits.dia-tss.plugins import clear
from gamera.toolkits.dia-tss.plugins import TextStringSep

# You can inherit from toolkit.CustomMenu to create a menu
# for your toolkit.  Create a list of menu option in the
# member _items, and a series of callback functions that
# correspond to them.  The name of the callback function
# should be the same as the menu item, prefixed by '_On'
# and with all spaces converted to underscores.
class Dia-tssMenu(toolkit.CustomMenu):
    _items = ["Dia-tss Toolkit",
              "Dia-tss Toolkit 2"]
    def _OnDia-tss_Toolkit(self, event):
        wxMessageDialog(None, "You clicked on Dia-tss Toolkit!").ShowModal()
        main.main()
    def _OnDia-tss_Toolkit_2(self, event):
        wxMessageDialog(None, "You clicked on Dia-tss Toolkit 2!").ShowModal()
        main.main()
dia-tss_menu = Dia-tssMenu()
