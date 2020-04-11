#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

from functools import partial

from PyQt5.Qt import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel

from calibre import prints
from calibre_plugins.SaveVirtualLibrariesToColumnGUI.config import namespace, column_name_pref, get_prefs

class SaveVirtualLibrariesToColumnGUIDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        # The current database shown in the GUI
        self.db = gui.current_db.new_api

        self.l = QVBoxLayout()
        self.setLayout(self.l)

        self.name = 'Save Book VLs To Column'
        self.setWindowTitle(self.name)
        self.setWindowIcon(icon)

        self.run_it_button = QPushButton('Run it', self)
        self.run_it_button.clicked.connect(partial(self.run_it, self))
        self.l.addWidget(self.run_it_button)

        self.conf_button = QPushButton(
                'Configure this plugin', self)
        self.conf_button.clicked.connect(self.config)
        self.l.addWidget(self.conf_button)

        self.resize(self.sizeHint())
        
    def run_it(self, parent, show_status_dialog):
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
            for lib, expr in libraries.items():
                books = db.search(expr)
                for book in books:
                    ans[book].add(lib)
            for s in current.keys():
                if set(current[s]) == set(ans[s]):
                    del ans[s]
            db.set_field(column_key, ans)
            msg = 'Updated column {0} for {1} books in {2}'.format(column_key, 
                        len(ans), now() - start_time)
            if show_status_dialog:
                info_dialog(parent, self.name, msg, show=True)
            prints('SaveVirtualLibrariesToColumnGUI', msg)
        else:
            error_dialog(parent, self.name, 'No lookup key has been provided', show=True)
            
    def config(self):
        self.do_user_config()

