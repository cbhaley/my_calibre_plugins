#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__   = "GPL v3"
__copyright__ = "2016, Charles Haley"
__docformat__ = "restructuredtext en"

from calibre.customize import LibraryClosedPlugin
import os, json

namespace = 'SaveVirtualLibrariesToColumnGUI'
json_pref = 'all_preferences'
column_name_pref = 'column_name'
    
def get_prefs(db):
    prefs = db.backend.prefs
    return json.loads(prefs.get_namespaced(namespace, json_pref, '{}'))

def set_prefs(db, d):
    prefs = db.backend.prefs
    prefs.set_namespaced(namespace, json_pref, json.dumps(d))
        
class SaveVirtualLibrariesToColumn(LibraryClosedPlugin):
    name = 'Save Virtual Libraries To Column'
    description = 'Save the names of the virtual libraries containing a book in a tags-like custom column'
    author = 'Charles Haley'
    supported_platforms = ['windows', 'osx', 'linux']
    version = (2, 0, 1)
    minimum_calibre_version = (2, 54, 0)
    

    def is_customizable(self):
        return True
    
    def config_widget(self):
        try:
            from PyQt5.Qt import QLabel, QLineEdit, QGridLayout, QWidget
            from calibre.gui2.ui import get_gui

            current_val = get_prefs(get_gui().current_db.new_api).get(column_name_pref, '')
            l = QGridLayout()
            l.addWidget(QLabel('lookup key for custom column to update:'), 0, 0)
            w = QLineEdit()
            w.setText(current_val)
            l.addWidget(w, 0, 1)
            w = QWidget()
            w.setLayout(l)
            return w
        except:
            import traceback
            traceback.print_exc()
        
    def save_settings(self, config_widget):
        from calibre.gui2.ui import get_gui
        from calibre.gui2 import error_dialog

        gui = get_gui()
        db = gui.current_db.new_api

        l = config_widget.layout()
        w = l.itemAtPosition(0, 1).widget()
        t = w.text()
        if t:
            fm = db.field_metadata
            if not t in fm:
                error_dialog(None, 'Undefined column', 'Column ' + t + 
                ' does not exist in the library', show=True)
                return
            if not fm[t]['is_multiple']:
                error_dialog(None, 'Column has wrong type', 'Column ' + t + 
                ' must be of type comma-separated text', show=True)
                return
        d = {}
        d[column_name_pref] = t             
        set_prefs(db, d)

    def run(self, db):
        from calibre.utils.date import now
        
        start_time = now()
        column_key = get_prefs(db).get(column_name_pref, '')
        if column_key:
            libraries = db._pref('virtual_libraries', {})
            all_ids = db.all_book_ids()
            current = db.all_field_for(column_key, all_ids)
            ans = dict(map(lambda x: ((x , set())), all_ids))
            for lib, expr in libraries.items():
                books = db.search(expr)
                for book in books:
                    ans[book].add(lib)
            for s in current.keys():
                if set(current[s]) == set(ans[s]):
                    del ans[s]
            db.set_field(column_key, ans)
            print('plugin {0}: updated column {1} for {2} books in {3}'.format(
                    self.name, column_key, len(ans), now() - start_time))
        else:
            print('plugin {0}: processing disabled by configuration'.format(self.name))