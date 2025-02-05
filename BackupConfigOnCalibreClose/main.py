#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__   = "GPL v3"
__copyright__ = "2016, Charles Haley"
__docformat__ = "restructuredtext en"

from collections import defaultdict
import contextlib
from datetime import datetime, timedelta
import os
import shutil

from qt.core import (Qt, QGridLayout, QHBoxLayout, QIcon, QLabel, QLineEdit, QPushButton,
                     QSpinBox, QToolButton, QWidget)

from calibre import config_dir
from calibre.gui2 import choose_dir, open_local_file
from calibre.utils.config import JSONConfig
from calibre.utils.date import format_date, now, parse_date

from calibre_plugins.BackupConfigOnCalibreClose import pi_name

CONFIG_DIR = 'CONFIG_DIR'
NAME_PATTERN = 'NAME_PATTERN'
DATE_PATTERN = 'DATE_PATTERN'
FIRST_DAYS = 'FIRST_DAYS'
MORE_DAYS = 'MORE_DAYS'
HISTORY = 'HISTORY'

CONFIG_DIR_PARENT_PATTERN = '{config_dir_parent}'
CONFIG_FOLDER_PATTERN = '{config_folder_name}'
NAME_PATTERN_DEFAULT = f'backup-{CONFIG_FOLDER_PATTERN}'
DATE_PATTERN_DEFAULT = 'yyyy-MM-dd at hh-mm-ss'
FIRST_DAYS_DEFAULT = 3
MORE_DAYS_DEFAULT = 10


pi_name = 'Backup Configuration Folder'
plugin_prefs = JSONConfig(f'plugins/{pi_name}')
plugin_prefs.defaults[CONFIG_DIR] = CONFIG_DIR_PARENT_PATTERN
plugin_prefs.defaults[NAME_PATTERN] = NAME_PATTERN_DEFAULT
plugin_prefs.defaults[DATE_PATTERN] = DATE_PATTERN_DEFAULT
plugin_prefs.defaults[FIRST_DAYS] = FIRST_DAYS_DEFAULT
plugin_prefs.defaults[MORE_DAYS] = MORE_DAYS_DEFAULT
plugin_prefs.defaults[HISTORY] = list()

class BackupConfigOnCalibreCloseMain:
    name = pi_name
    description = 'Backup the current calibre configuration folder when calibre is closed'
    author = 'Charles Haley'
    supported_platforms = ['windows', 'osx', 'linux']
    version = (1, 0, 3)

    def is_customizable(self):
        return True

    def config_widget(self):
        mw = QWidget()
        l = QGridLayout()
        mw.setLayout(l)

        gr = 0 # row in the grid layout

        def add_row(layout, text, widget, row):
            layout.addWidget(QLabel(text), row, 0,
                             alignment=(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter))
            layout.addWidget(widget, row, 1)

        w = QLabel('Documentation is in tooltips')
        l.addWidget(w, gr, 1, 1, 2)
        gr += 1

        self.config_dir_widget = w = QLineEdit()
        self.config_dir_widget_tt = ('<p>The parent folder where the backup folder will be created. '
                                     'The value "{}" is replaced with the path to the folder containing '
                                     'the calibre configuration folder</p>'.format(CONFIG_DIR_PARENT_PATTERN))
        add_row(l, 'Containing folder:', w, gr)
        w = self.folder_button = QToolButton()
        w.setIcon(QIcon.ic('devices/folder.png'))
        w.setToolTip('Choose a folder')
        w.clicked.connect(self.choose_folder)
        l.addWidget(w, gr, 2)
        gr += 1
        w = self.config_dir_value = QLabel()
        add_row(l, 'Current value:', w, gr)
        gr += 1

        w = self.name_pattern_widget = QLineEdit()
        self.name_pattern_widget_tt = (
            '<p>The name of the folder that will contain the zip backup files. This folder '
            'will be created inside the folder named above (<i>Containing folder</i>). The value '
            '"{0}" is replaced with the base name of the configuration folder. The default is '
            '"backup-{0}" that becomes "backup-name_of_config_folder"</p><p></p>'.format(CONFIG_FOLDER_PATTERN))
        add_row(l, 'Backup folder name:', w, gr)
        gr += 1
        w = self.name_pattern_value = QLabel()
        add_row(l, 'Current value:', w, gr)
        gr += 1

        w = self.folder_path_value = QLabel()
        add_row(l, 'Full path to backups:', w, gr)
        gr += 1

        w = self.date_pattern_widget = QLineEdit()
        self.date_pattern_widget_tt = ('<p>A standard date pattern used as the name the backup file. '
                                      'The default is year-month-day at hours-minutes-seconds</p><p></p>')
        add_row(l, 'File name:', w, gr)
        gr += 1
        w = self.date_pattern_value = QLabel()
        add_row(l, 'Current value:', w, gr)
        gr += 1

        w = self.first_days_widget = QSpinBox()
        w.setValue(plugin_prefs[FIRST_DAYS])
        w.setMaximum(20)
        w.setToolTip('<p>Save all backup zip files for the number of days '
                     'specified here. You can set this to zero, in which case '
                     'only the last backup of a day will be saved</p>')
        add_row(l, 'Days to keep all backups:', w, gr)
        gr += 1

        w = self.more_days_widget = QSpinBox()
        w.setValue(plugin_prefs[MORE_DAYS])
        w.setMinimum(1)
        w.setToolTip('<p>Save the last backup file made during a day for the '
                                         'number of days specified here. This count starts after '
                                         'the number of "keep all backups" days specified above. '
                                         'If this value is set to one and "keep all backups" is '
                                         'zero, only one backup file will be kept.</p>')
        add_row(l, 'Days to keep last backup:', w, gr)
        gr += 1

        # Do this at the end so all the widgets exist when the signals are raised
        self.config_dir_widget.textChanged.connect(self.folder_pattern_changed)
        self.config_dir_widget.setText(plugin_prefs[CONFIG_DIR])
        self.name_pattern_widget.textChanged.connect(self.name_pattern_changed)
        self.name_pattern_widget.setText(plugin_prefs[NAME_PATTERN])
        self.date_pattern_widget.textChanged.connect(self.date_pattern_changed)
        self.date_pattern_widget.setText(plugin_prefs[DATE_PATTERN])

        # Add the buttons
        bl = QHBoxLayout()
        bl.addStretch()
        w = QPushButton('Reset to defaults')
        w.clicked.connect(self.reset_to_defaults)
        bl.addWidget(w)
        w = QPushButton('Open backup folder')
        w.clicked.connect(self.open_backup_folder)
        bl.addWidget(w)
        bl.addStretch()
        l.addLayout(bl, gr, 1)
        gr += 1

        l.setRowStretch(gr, 10)
        return mw

    def choose_folder(self):
        from calibre.gui2.ui import get_gui
        gui = get_gui()
        f = choose_dir(gui, 'backup config on close', 'Select parent folder')
        if not f:
            return
        self.config_dir_widget.setText(f)

    def open_backup_folder(self):
        c,d,_ = self.get_expanded_patterns()
        open_local_file(os.path.join(c, d))

    def get_expanded_patterns(self):
        conf_dir = self.config_dir_widget.text().strip().replace(CONFIG_DIR_PARENT_PATTERN,
                                                                 os.path.dirname(config_dir))
        name = self.name_pattern_widget.text().strip().replace(CONFIG_FOLDER_PATTERN,
                                                               os.path.basename(config_dir))
        date = format_date(now(), self.date_pattern_widget.text().strip())
        return (conf_dir, name, date)

    def folder_pattern_changed(self, _):
        p,f,_ = self.get_expanded_patterns()
        tt = self.config_dir_widget_tt + '</p><p>Current value: "' + p + '"</p>'
        self.config_dir_widget.setToolTip(tt)
        self.config_dir_value.setText(p)
        self.folder_path_value.setText(os.path.join(p, f))

    def name_pattern_changed(self, _):
        p,f,_ = self.get_expanded_patterns()
        tt = self.name_pattern_widget_tt + '</p><p>Current value: "' + f + '"</p>'
        self.name_pattern_widget.setToolTip(tt)
        self.name_pattern_value.setText(f)
        self.folder_path_value.setText(os.path.join(p, f))


    def date_pattern_changed(self, _):
        _,_,fn = self.get_expanded_patterns()
        tt = self.date_pattern_widget_tt + '</p><p>Current value: "' + fn + '"</p>'
        self.date_pattern_widget.setToolTip(tt)
        self.date_pattern_value.setText(fn)

    def reset_to_defaults(self):
        self.config_dir_widget.setText(CONFIG_DIR_PARENT_PATTERN)
        self.name_pattern_widget.setText(NAME_PATTERN_DEFAULT)
        self.date_pattern_widget.setText(DATE_PATTERN_DEFAULT)
        self.first_days_widget.setValue(FIRST_DAYS_DEFAULT)
        self.more_days_widget.setValue(MORE_DAYS_DEFAULT)

    def save_settings(self):
        plugin_prefs[CONFIG_DIR] = self.config_dir_widget.text()
        plugin_prefs[NAME_PATTERN] = self.name_pattern_widget.text()
        plugin_prefs[DATE_PATTERN] = self.date_pattern_widget.text()
        plugin_prefs[FIRST_DAYS] = self.first_days_widget.value()
        plugin_prefs[MORE_DAYS] = self.more_days_widget.value()

    def run(self):
        from calibre.gui2.ui import get_gui
        gui = get_gui()
        if gui is None:
            return  # not in the GUI
        if getattr(gui, 'restart_after_quit', False):
            return  # restarting after config change. Don't save the backup
        if not gui.shutting_down:
            return  # This is a change library, not a shutdown.

        parent = plugin_prefs[CONFIG_DIR].strip().replace(CONFIG_DIR_PARENT_PATTERN, os.path.dirname(config_dir))
        folder = plugin_prefs[NAME_PATTERN].strip().replace(CONFIG_FOLDER_PATTERN, os.path.basename(config_dir))
        in_dir = os.path.join(parent, folder)

        # The loop is for testing history deletion. It builds a number of
        # backups marked in history as 10 hours apart. Leave it here with a
        # range of 1 in case it is needed
        for i in range(1):
            # Do the work. First generate the path and file names.
            file = plugin_prefs[DATE_PATTERN].strip()
            td = timedelta(hours = i * 10)
            file = format_date(now() - td, file)

            # Make the folders if needed
            os.makedirs(in_dir, exist_ok=True)
            # Write the archive
            to_file = os.path.join(in_dir, file)
            shutil.make_archive(to_file, 'zip', config_dir)
            print(f'[{pi_name}]: wrote config backup to {to_file}.zip')
            # Update the history list of backups
            history = plugin_prefs[HISTORY]
            history.append((str(now()-td), file + '.zip'))
            plugin_prefs[HISTORY] = history
        if i > 1:  # The loop was used
            return

        # Clean up history. This is made complicated because we want to use
        # calendar days, which means placing timestamps into a "day". This
        # problem is solved by converting the date to its "ordinal", which is
        # the number of days since the Gregorian calendar started. By processing
        # the entries in date order we can keep or delete based on the number of
        # days from today (today's ordinal).

        history = sorted(plugin_prefs[HISTORY], key=lambda t: t[0], reverse=True)
        now_ord = datetime.toordinal(now())
        first_days_ord = now_ord - plugin_prefs[FIRST_DAYS]
        more_days_ord = now_ord - (plugin_prefs[FIRST_DAYS] + plugin_prefs[MORE_DAYS])

        md_items = defaultdict(list)
        new_history = []
        for date,file in history:
            date_ord = datetime.toordinal(parse_date(date))
            if date_ord > first_days_ord:
                # This entry happened in the "keep all" window. Keep it
                new_history.append((date, file))
                continue
            if date_ord > more_days_ord:
                # This one is in the "keep some" window. Record it for further processing
                md_items[date_ord].append((date, file))
                continue
            # It is beyond the windows. Delete it
            print(f'[{pi_name}]: Deleting old config backup file {file}')
            with contextlib.suppress(FileNotFoundError):
                os.remove(os.path.join(in_dir, file))

        # Keep the last one of the day for "more" days
        for l in tuple(md_items.values()):
            new_history.append(l[0])
            for date,file in l[1:]:
                print(f'[{pi_name}]: Deleting old config backup file {file}')
                with contextlib.suppress(FileNotFoundError):
                    os.remove(os.path.join(in_dir, file))
        plugin_prefs[HISTORY] = new_history
