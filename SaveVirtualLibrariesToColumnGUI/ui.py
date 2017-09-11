#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

from functools import partial
from calibre import prints

# The class that all interface action plugins must inherit from
from calibre.gui2.actions import InterfaceAction
from calibre.gui2.device import device_signals
from calibre_plugins.SaveVirtualLibrariesToColumnGUI.main import SaveVirtualLibrariesToColumnGUIDialog
from calibre_plugins.SaveVirtualLibrariesToColumnGUI.config import get_prefs, run_on_disconnect_pref
from calibre_plugins.SaveVirtualLibrariesToColumnGUI.common_utils import set_plugin_icon_resources, get_icon
from PyQt5.Qt import QAction, QMenu

# The icon came from http://www.iconarchive.com/show/my-seven-icons-by-itzikgur/Books-1-icon.html
# Freeware license

class SaveVirtualLibrariesToColumnGUI(InterfaceAction):

    name = 'Save Book VLs To Column'

    action_spec = (name, None, 'Run Save Book VLs To Column', (()))
	
	icon_name = 'images/icon.png'

    def genesis(self):
		# Read the plugin icons and store for potential sharing with the config widget
        icon_resources = self.load_resources(self.icon_name)
        set_plugin_icon_resources(self.name, icon_resources)
	
        self.qaction.triggered.connect(self.show_dialog)
		
		self.menu = QMenu(self.gui)
		
		self.config_action = self.menu.addAction("Configure")
		self.config_action.triggered.connect(self.config)		
		
		self.run_action = self.menu.addAction("Run")
        self.gui.addAction(self.run_action)
        self.gui.keyboard.register_shortcut('Run Save Book VLs To Column', 
					 _('Run Save Book VLs To Column'),
                     description=_('Run Save Book VLs To Column'),
                     action=self.run_action,
                     group=self.action_spec[0])
		self.run_action.triggered.connect(self.run_it)
		
		self.qaction.setMenu(self.menu)
		self.qaction.setIcon(get_icon(self.icon_name))
		self.dialog = None
		device_signals.device_connection_changed.connect(self.device_connection_changed)

	def device_connection_changed(self, is_connected):
		prints('SaveVirtualLibrariesToColumnGUI', 'device connected', is_connected)
		if not is_connected:
			p = get_prefs()
			if p.get(run_on_disconnect_pref, False):
				self.dialog = SaveVirtualLibrariesToColumnGUIDialog(self.gui, get_icon(self.icon_name), self.config)
				self.dialog.run_it(self.dialog.gui, False)

    def show_dialog(self):
        self.dialog = SaveVirtualLibrariesToColumnGUIDialog(self.gui, get_icon(self.icon_name), self.config)		
        self.dialog.show()
		
    def run_it(self):
        self.dialog = SaveVirtualLibrariesToColumnGUIDialog(self.gui, get_icon(self.icon_name), self.config)
        self.dialog.run_it(self.dialog.gui, True)

	def config(self):
		self.interface_action_base_plugin.do_user_config()
