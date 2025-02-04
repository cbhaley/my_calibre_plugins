#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Grant Drake <grant.drake@gmail.com>'
__docformat__ = 'restructuredtext en'

from calibre.utils.config import JSONConfig
try:
    from PyQt5.Qt import (QWidget, QGridLayout, QGroupBox,  QVBoxLayout, QCheckBox)
except ImportError:
    from PyQt4.Qt import (QWidget, QGridLayout, QGroupBox,  QVBoxLayout, QCheckBox)

STORE_SAVED_SETTINGS = 'SavedSettings'
STORE_NAME = 'Options'
KEY_ASK_FOR_CONFIRMATION = 'askForConfirmation'

DEFAULT_STORE_VALUES = {
                        KEY_ASK_FOR_CONFIRMATION : True
                       }

# This is where all preferences for this plugin will be stored
plugin_prefs = JSONConfig('plugins/Modify ePub')

# Set defaults
plugin_prefs.defaults[STORE_SAVED_SETTINGS] = []
plugin_prefs.defaults[STORE_NAME] = DEFAULT_STORE_VALUES

class ConfigWidget(QWidget):

    def __init__(self, plugin_action):
        QWidget.__init__(self)
        self.plugin_action = plugin_action
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        c = plugin_prefs[STORE_NAME]
        ask_for_confirmation = c.get(KEY_ASK_FOR_CONFIRMATION, DEFAULT_STORE_VALUES[KEY_ASK_FOR_CONFIRMATION])
        
        other_group_box = QGroupBox('Other options:', self)
        layout.addWidget(other_group_box)
        other_group_box_layout = QGridLayout()
        other_group_box.setLayout(other_group_box_layout)

        self.ask_for_confirmation_checkbox = QCheckBox('Prompt to save epubs', self)
        self.ask_for_confirmation_checkbox.setToolTip('Uncheck this option if you want changes applied without\n'
                                                      'a confirmation dialog. There is a small risk with this\n'
                                                      'option unchecked that if you are making other changes to\n'
                                                      'this book record at the same time they will be lost.')
        self.ask_for_confirmation_checkbox.setChecked(ask_for_confirmation)
        other_group_box_layout.addWidget(self.ask_for_confirmation_checkbox, 0, 0, 1, 3)
        
    def save_settings(self):
        new_prefs = {}
        new_prefs[KEY_ASK_FOR_CONFIRMATION] = self.ask_for_confirmation_checkbox.isChecked()
        plugin_prefs[STORE_NAME] = new_prefs
