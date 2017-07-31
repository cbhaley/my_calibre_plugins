#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__   = "GPL v3"
__copyright__ = "2016, Charles Haley"
__docformat__ = "restructuredtext en"

from calibre.customize import LibraryClosedPlugin
import os

class SaveCompositeCustomColumns(LibraryClosedPlugin):
	name = 'Save Composite Custom Columns'
	description = 'Store values of columns "built from other columns" for use by apps that read the calibre database, for example Calibre Companion'
	author = 'Charles Haley'
	supported_platforms = ['windows', 'osx', 'linux']
	version = (1, 1, 0)
	
	namespace = 'CompositeColumnValues'
	library_key_prefix = 'processLib-'
	
	def is_customizable(self):
        return True
	
	def config_widget(self):
		from PyQt5.Qt import QCheckBox
		from calibre.gui2.ui import get_gui
		
		gui = get_gui()
		db = gui.current_db.new_api
		prefs = db.backend.prefs
		current_prefs = prefs.get_namespaced(self.namespace, 'process_libraries', {})
		current_library = db.backend.library_path
		w = QCheckBox('Run plugin on library ' + db.backend.library_path)
		w.setChecked(current_prefs.get(self.library_key_prefix + current_library, True))
		return w
		
	def save_settings(self, config_widget):
		from calibre.gui2.ui import get_gui

		gui = get_gui()
		db = gui.current_db.new_api
		prefs = db.backend.prefs
		current_prefs = prefs.get_namespaced(self.namespace, 'process_libraries', {})
		current_library = db.backend.library_path

		current_prefs[self.library_key_prefix + current_library] = config_widget.isChecked()
		prefs.set_namespaced(self.namespace, 'process_libraries', current_prefs)

	def run(self, db):
		from calibre.utils.date import now, UNDEFINED_DATE, parse_date
		import apsw

		prefs = db.backend.prefs
		current_library = db.backend.library_path
		current_prefs = prefs.get_namespaced(self.namespace, 'process_libraries', {})
		if current_prefs.get(self.library_key_prefix + current_library, True):
			updated_books = 0
			start_time = now()
			composites = set()
			for key, meta in db.field_metadata.custom_iteritems():
				if meta.get('datatype') == 'composite':
					composites.add(key)
			if composites:
				all_ids = db.all_book_ids()
				updated_books = len(all_ids)
				all_books_composites = {}
				for id_ in all_ids:
					mi = db.get_proxy_metadata(id_)
					composites_for_book = dict()
					composites_for_book['last_modified'] = unicode(mi.get('last_modified'))
					for key in composites:
						val = mi.get(key)
						composites_for_book[key] = val
					all_books_composites[id_] = composites_for_book
				db.add_custom_book_data(self.namespace, all_books_composites, delete_first=True)
			print('plugin {0} library {1}: updated {2} books in {3}'.format(
					self.name, current_library, updated_books, now() - start_time))
		else:
			db.delete_custom_book_data(self.namespace)
			print('plugin {0} library {1}: processing disabled by configuration'.format(
					self.name, current_library))