#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

from functools import partial

# The class that all interface action plugins must inherit from
from calibre.gui2.actions import InterfaceAction
from calibre_plugins.SaveVirtualLibrariesToColumnGUI.main import SaveVirtualLibrariesToColumnGUIDialog
from PyQt5.Qt import QAction

class SaveVirtualLibrariesToColumnGUI(InterfaceAction):

    name = 'Save Book VLs To Column'

    action_spec = (name, None, 'Run Save Book VLs To Column', (()))

    def genesis(self):
        self.qaction.triggered.connect(partial(self.show_dialog, False))
		
		self.run_action = QAction(self.gui)
        self.gui.addAction(self.run_action)
        self.gui.keyboard.register_shortcut('Run Save Book VLs To Column', 
					 _('Run Save Book VLs To Column'),
                     description=_('Run Save Book VLs To Column'),
                     action=self.run_action,
                     group=self.action_spec[0])
		self.run_action.triggered.connect(partial(self.show_dialog, True))

    def show_dialog(self, run_it):
        base_plugin_object = self.interface_action_base_plugin
        do_user_config = base_plugin_object.do_user_config
        d = SaveVirtualLibrariesToColumnGUIDialog(self.gui, do_user_config, run_it)
        d.show()
