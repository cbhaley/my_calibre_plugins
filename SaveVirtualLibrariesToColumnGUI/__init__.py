#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

from calibre.customize import InterfaceActionBase

class SaveVirtualLibrariesToColumnGUI(InterfaceActionBase):
    '''
    This class is a simple wrapper that provides information about the actual
    plugin class. The actual interface plugin class is called InterfacePlugin
    and is defined in the ui.py file, as specified in the actual_plugin field
    below.

    The reason for having two classes is that it allows the command line
    calibre utilities to run without needing to load the GUI libraries.
    '''
    name                = 'Save Virtual Libraries To Column GUI'
    description         = ('For each book in the library, compute the list of virtual libraries '
							'containing that book then save that list to a custom column')
    supported_platforms = ['windows', 'osx', 'linux']
    author              = 'Charles Haley'
    version             = (2, 1, 0)
    minimum_calibre_version = (2, 54, 0)

    #: This field defines the GUI plugin class that contains all the code
    #: that actually does something. Its format is module_path:class_name
    #: The specified class must be defined in the specified module.
    actual_plugin       = 'calibre_plugins.SaveVirtualLibrariesToColumnGUI.ui:SaveVirtualLibrariesToColumnGUI'

    def is_customizable(self):
        '''
        This method must return True to enable customization via
        Preferences->Plugins
        '''
        return True

    def config_widget(self):
        from calibre_plugins.SaveVirtualLibrariesToColumnGUI.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()

