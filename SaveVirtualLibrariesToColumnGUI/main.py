#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

from PyQt5.Qt import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel

from calibre_plugins.SaveVirtualLibrariesToColumnGUI.config import namespace, column_name_pref, get_prefs

class SaveVirtualLibrariesToColumnGUIDialog(QDialog):

    def __init__(self, gui, do_user_config, run_it_flag):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        # The current database shown in the GUI
        self.db = gui.current_db.new_api

        self.l = QVBoxLayout()
        self.setLayout(self.l)

		self.name = 'Save Book VLs To Column'
        self.setWindowTitle(self.name)

        self.run_it_button = QPushButton('Run it', self)
        self.run_it_button.clicked.connect(self.run_it)
        self.l.addWidget(self.run_it_button)

        self.conf_button = QPushButton(
                'Configure this plugin', self)
        self.conf_button.clicked.connect(self.config)
        self.l.addWidget(self.conf_button)

        self.resize(self.sizeHint())
		
		self.run_it_flag = run_it_flag

	def show(self):
		QDialog.show(self)
		if self.run_it_flag:
			self.run_it()
			self.accept()

	def run_it(self):
		from calibre.utils.date import now
		from calibre.gui2 import error_dialog, info_dialog
		
		start_time = now()

		db = self.db
		column_key = get_prefs().get(column_name_pref, '')
		
		if column_key:
			libraries = db._pref('virtual_libraries', {})
			all_ids = db.all_book_ids()
			current = db.all_field_for(column_key, all_ids)
			ans = dict(map(lambda x: (x, set()), all_ids))
			for lib, expr in libraries.iteritems():
				books = db.search(expr)
				for book in books:
					ans[book].add(lib)
			for s in current.iterkeys():
				if set(current[s]) == set(ans[s]):
					del ans[s]
			db.set_field(column_key, ans)
			info_dialog(self, self.name, 
				'Updated column {0} for {1} books in {2}'.format(column_key, 
						len(ans), now() - start_time),
				show=True)
		else:
			error_dialog(self, self.name, 'No lookup key has been provided', show=True)
			
    def config(self):
        self.do_user_config(parent=self)

