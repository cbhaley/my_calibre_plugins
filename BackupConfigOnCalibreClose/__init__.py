#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__   = "GPL v3"
__copyright__ = "2016, Charles Haley"
__docformat__ = "restructuredtext en"

from calibre.customize import LibraryClosedPlugin

pi_name = 'Backup Configuration Folder'

class BackupConfigOnCalibreClose(LibraryClosedPlugin):
    name = pi_name
    description = 'Backup the current calibre configuration folder when calibre is closed'
    author = 'Charles Haley'
    supported_platforms = ['windows', 'osx', 'linux']
    version = (1, 1, 0)
    minimum_calibre_version = (5, 35, 0)

    def __init__(self, plugin_path):
        super().__init__(plugin_path)
        from calibre_plugins.BackupConfigOnCalibreClose.main import BackupConfigOnCalibreCloseMain
        self.main = BackupConfigOnCalibreCloseMain()

    def is_customizable(self):
        return True

    def config_widget(self):
        return self.main.config_widget()

    def save_settings(self, _):
        self.main.save_settings()

    def run(self, _):
        self.main.run()