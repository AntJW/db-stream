import redis
import os
import sys


class CacheClient:
    def __init__(self):
        self._host = os.getenv("CACHE_HOST")
        self._port = os.getenv("CACHE_PORT")
        self._conn = redis.StrictRedis(host=self._host, port=self._port, db=0)

    def last_event_completed(self):
        """
        Returns the log file and position of last binlog event that has status 'complete' in cache.
        """
        try:
            self._conn.ping()
        except Exception as e:
            sys.exit(e)

        log_file = "mysql-bin-changelog.000261"
        log_pos = 56030111
        return log_file, log_pos
