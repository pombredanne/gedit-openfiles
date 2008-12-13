from gedit import Plugin
from FileMonitor import FileMonitor
from DBWrapper import DBWrapper
from GeditOpenFileGui import GeditOpenFileGui
from Logger import log


class GeditOpenFile(Plugin):
    DATA_TAG = "GeditOpenFilePlugin"

    def __init__(self):
        Plugin.__init__(self)

        # Create DB Wrapper and start the thread
        self._db_wrapper = DBWrapper()
        #TODO Gett Root from file_browser
        self._file_monitor = FileMonitor(self._db_wrapper, ".")

    def _get_instance( self, window ):
        return window.get_data( self.DATA_TAG )

    def _set_instance( self, window, instance ):
        window.set_data( self.DATA_TAG, instance )

    def activate( self, window ):
        log.debug("[GeditOpenFile] Activate")
        self._set_instance( window, GeditOpenFileGui(self, window, self._db_wrapper))

    def deactivate( self, window ):
        self._get_instance( window ).deactivate()
        self._set_instance( window, None )

    def update_ui( self, window ):
        self._get_instance( window ).update_ui()
