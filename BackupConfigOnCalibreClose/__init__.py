#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

__license__   = "GPL v3"
__copyright__ = "2025, Charles Haley"
__docformat__ = "restructuredtext en"

try:
    load_translations()
except NameError:
    pass # load_translations() added in calibre 1.9

from calibre.customize import LibraryClosedPlugin


class BackupConfigOnCalibreClose(LibraryClosedPlugin):
    name = 'Backup Configuration Folder'
    description = _('Backup the current calibre configuration folder when calibre is closed')
    author = 'Charles Haley'
    supported_platforms = ['windows', 'osx', 'linux']
    version = (1, 1, 2)
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