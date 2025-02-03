#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__   = "GPL v3"
__copyright__ = "2016, Charles Haley"
__docformat__ = "restructuredtext en"

import os
import shutil

from qt.core import QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget

from calibre import config_dir
from calibre.customize import LibraryClosedPlugin
from calibre.utils.config import JSONConfig
from calibre.utils.date import format_date, now

CONFIG_DIR = 'CONFIG_DIR'
NAME_PATTERN = 'NAME_PATTERN'
DATE_PATTERN = 'DATE_PATTERN'

CONFIG_DIR_PARENT_PATTERN = '{config_dir_parent}'
CONFIG_FOLDER_PATTERN = '{config_folder_name}'
NAME_PATTERN_DEFAULT = f'backup-{CONFIG_FOLDER_PATTERN}'
DATE_PATTERN_DEFAULT = 'yyyy-MM-dd at hh-mm-ss'

pi_name = 'Backup Configuration Folder'
plugin_prefs = JSONConfig(f'plugins/{pi_name}')
plugin_prefs.defaults[CONFIG_DIR] = CONFIG_DIR_PARENT_PATTERN
plugin_prefs.defaults[NAME_PATTERN] = NAME_PATTERN_DEFAULT
plugin_prefs.defaults[DATE_PATTERN] = DATE_PATTERN_DEFAULT


class BackupConfigOnCalibreClose(LibraryClosedPlugin):
    name = pi_name
    description = 'Backup the calibre configuration folder when calibre is closed'
    author = 'Charles Haley'
    supported_platforms = ['windows', 'osx', 'linux']
    version = (1, 0, 0)

    def is_customizable(self):
        return True

    def config_widget(self):
        mw = QWidget()
        l = QFormLayout()
        l.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        mw.setLayout(l)
        l.addRow(QLabel('Documentation is in tooltips'))
        self.config_dir_widget = w = QLineEdit()
        w.setText(plugin_prefs[CONFIG_DIR])
        w.setToolTip('<p>The parent folder where the backup folder will be created. '
                     'The default is the folder containing the calibre configuration folder</p>')
        l.addRow('Destination folder:', w)
        self.name_pattern_widget = w = QLineEdit()
        w.setText(plugin_prefs[NAME_PATTERN])
        w.setToolTip('<p>The name of the backup folder that will contain the zip backup files. '
                     'The default is "backup-" followed by the name of the calibre configuration folder</p>')
        l.addRow('File name pattern:', w)
        self.date_pattern_widget = w = QLineEdit()
        w.setText(plugin_prefs[DATE_PATTERN])
        w.setToolTip('<p>A standard date pattern. The default is year-month-day at hours-minutes-seconds</p>')
        l.addRow('Date pattern:', w)

        bl = QHBoxLayout()
        bl.addStretch()
        w = QPushButton('Reset to defaults')
        w.clicked.connect(self.reset_to_defaults)
        bl.addWidget(w)
        bl.addStretch()
        l.addRow(bl)
        return mw

    def reset_to_defaults(self):
        self.config_dir_widget.setText(CONFIG_DIR_PARENT_PATTERN)
        self.name_pattern_widget.setText(NAME_PATTERN_DEFAULT)
        self.date_pattern_widget.setText(DATE_PATTERN_DEFAULT)

    def save_settings(self, config_widget):
        plugin_prefs[CONFIG_DIR] = self.config_dir_widget.text()
        plugin_prefs[NAME_PATTERN] = self.name_pattern_widget.text()
        plugin_prefs[DATE_PATTERN] = self.date_pattern_widget.text()

    def run(self, db):
        from calibre.gui2.ui import get_gui
        gui = get_gui()
        if gui is None:
            return  # not in the GUI
        if getattr(gui, 'restart_after_quit', False):
            return  # restarting after config change. Don't save the backup
        if not gui.shutting_down:
            return  # This is a change library, not a shutdown.

        # Do the work. First generate the path and file names.
        parent = plugin_prefs[CONFIG_DIR]
        parent = parent.replace(CONFIG_DIR_PARENT_PATTERN, os.path.dirname(config_dir))
        folder = plugin_prefs[NAME_PATTERN]
        folder = folder.replace(CONFIG_FOLDER_PATTERN, os.path.basename(config_dir))
        file = plugin_prefs[DATE_PATTERN]
        file = format_date(now(), file)

        # Make the folders if needed
        to_dir = os.path.join(parent, folder)
        os.makedirs(to_dir, exist_ok=True)
        # Write the archive
        to_file = os.path.join(to_dir, file)
        shutil.make_archive(to_file, 'zip', config_dir)
