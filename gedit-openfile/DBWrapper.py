"""
Provides the DBWrapper Class which currently wraps sqlite in order to provide
some abstractions an multithreading support.
"""
import os
import sqlite3
from Logger import log
from threading import Thread
from Queue import Queue
from FileMonitor import FileWrapper


class DBWrapper(Thread):
    """
    Class to wrap the python sqlite3 module to support multithreading
    """

    def __init__(self):
        # Create Database and a queue
        Thread.__init__(self)
        self._queue = Queue()
        self.start()

    def run(self):
        self._create_db()
        while True:
            if not self._queue.empty():
                sql, result = self._queue.get()
                log.info("QUERY: %s" % sql)
                log.info("RESULT: " + str(result))
                cursor = self._db.cursor()
                cursor.execute(sql)
                    
                if result:
                    log.info("Putting Results")
                    for row in cursor.fetchall():
                        result.put(row)
                    result.put("__END__")
                
                self._db.commit()

    def execute(self, sql, params=None, result=None):
        if params:
            self._queue.put((sql % params, result))
        else:
            self._queue.put((sql, result))

    def select(self, sql, params=None):
        list_result = []
        result = Queue()
        log.info("Params: " + params)
        if params:
            log.debug("QUERY with params")
            self.execute(sql, params, result)
        else:
            log.debug("QUERY with out params")
            self.execute(sql, result=result)

        while True:
            row = result.get()
            if row == '__END__': break
            list_result.append(row)
        log.info("SELECT RESULT COUNT: " + str(len(list_result)))
        return list_result
    
    def select_on_filename(self, query_input):
        log.info("[DBWrapper] select_on_filename method")
        query_param = "%"+query_input.replace(" ", "%")+"%"
        results = []
        res = self.select("SELECT name, path FROM files WHERE path LIKE '%s' LIMIT 51", query_param)
        for row in res:
            results.append(FileWrapper(query_input, row[0], row[1]))
        return results

    def close(self):
        self._queue.put("__CLOSE__")

    def _create_db(self):
        self._db = sqlite3.connect(":memory:")
        self.execute("CREATE TABLE files ( id AUTO_INCREMENT PRIMARY KEY, " +
            "path VARCHAR(255), name VARCHAR(255), " +
            "open_count INTEGER DEFAULT 0)")

    def add_file(self, path, name):
        path = os.path.join(path, name)
        log.debug("[DBWrapper] Adding File: " + path)
        self.execute("INSERT INTO files (name, path) VALUES ('%s', '%s')",
            (name, path))

    def remove_file(self, path, name):
        path = os.path.join(path, name)
        log.debug("[DBWrapper] Removing File: " + path)
        self.execute("DELETE FROM files where path = '%s'", (path, ))

    def remove_dir(self, path):
        log.debug("[DBWrapper] Remove Dir: " + path)
        self.execute("DELETE FROM files WHERE path like '%s'", (path+"%",))

if __name__ == '__main__':
    db = DBWrapper()
    db.execute("INSERT INTO files (path, name) VALUES ('%s', '%s')",
         ("vbabiy", "/home/vbabiy"))
    print (db.select("SELECT * FROM files"))
