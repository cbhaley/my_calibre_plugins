#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

import json

from PyQt5.Qt import QWidget, QGridLayout, QLabel, QComboBox, QCheckBox

from calibre.utils.config import JSONConfig
from calibre.gui2.ui import get_gui

namespace = 'SaveVirtualLibrariesToColumnGUI'
json_pref = 'all_preferences'
column_name_pref = 'column_name'
run_on_disconnect_pref = 'run_on_disconnect'

def get_prefs():
	db = get_gui().current_db.new_api
	prefs = db.backend.prefs
	return json.loads(prefs.get_namespaced(namespace, json_pref, '{}'))

def set_prefs(d):
	db = get_gui().current_db.new_api
	prefs = db.backend.prefs
    prefs.set_namespaced(namespace, json_pref, json.dumps(d))

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QGridLayout()
        self.setLayout(self.l)

        self.label = QLabel('Lookup key of column:')
        self.l.addWidget(self.label, 0, 0)

		db = get_gui().current_db.new_api
		d = get_prefs()

		key = d.get(column_name_pref, None)
		
        self.fields = QComboBox(self)
		fm = db.field_metadata
		current_idx = 1;
		found_idx = 0;
		self.fields.addItem('')
		for col in fm.custom_field_keys(include_composites=False):
			if fm[col]['datatype'] == 'text' and fm[col]['is_multiple']:
				self.fields.addItem(col)
				if key == col:
					found_idx = current_idx
				current_idx += 1
		self.fields.setCurrentIndex(found_idx)
        self.l.addWidget(self.fields, 0 ,1)
        self.label.setBuddy(self.fields)
		
		self.run_on_disconnect = QCheckBox('Run plugin when a device disconnects')
		self.run_on_disconnect.setChecked(d.get(run_on_disconnect_pref, False))
		self.l.addWidget(self.run_on_disconnect, 1, 0, 1, 2)

    def save_settings(self):
		d = {}
		d[column_name_pref] = self.fields.currentText()
		d[run_on_disconnect_pref] = self.run_on_disconnect.isChecked()
		set_prefs(d)