#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Grant Drake <grant.drake@gmail.com>'
__docformat__ = 'restructuredtext en'

# calibre Python 3 compatibility.
import six
from six import text_type as unicode

try:
    from PyQt5.Qt import QDialog, QAbstractItemView, QDialogButtonBox, QListWidgetItem, \
                     QListWidget, QVBoxLayout
except ImportError:
    from PyQt4.Qt import QDialog, QAbstractItemView, QDialogButtonBox, QListWidgetItem, \
                     QListWidget, QVBoxLayout
from calibre_plugins.user_category.common_utils import get_icon

class ChooseMultipleDialog(QDialog):

    def __init__(self, parent=None, values=[], action='', label='', icon=''):
        QDialog.__init__(self, parent)
        self.setWindowTitle('Select values to ' + action)
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.values_list = QListWidget(self)
        self.values_list.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.values_list)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.resize(self.sizeHint())

        for value in values:
            self.values_list.addItem(QListWidgetItem(get_icon(icon), value))
        self.values_list.selectAll()

    @property
    def selected_values(self):
        values = []
        for item in self.values_list.selectedItems():
            values.append(unicode(item.text()))
        return values
