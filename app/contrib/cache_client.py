import redis
import os
import sys


class CacheClient:
    def __init__(self):
        self._service_id = os.getenv("SERVICE_ID")
        self._host = os.getenv("CACHE_HOST")
        self._port = os.getenv("CACHE_PORT")
        self._conn = redis.StrictRedis(host=self._host, port=self._port, decode_responses=True, db=0)

    def get_position(self):
        """
        Returns the log file and position of last binlog event that has status 'complete' in cache.
        """
        try:
            data = self._conn.hgetall(self._service_id)
            log_file = data["log_file"]
            log_pos = int(data["log_pos"])
        except KeyError:
            log_file = ""
            log_pos = None
        except Exception as e:
            sys.exit(e)

        return log_file, log_pos

    def set_position(self, log_file, log_pos):
        """
        Updates cache with the last successful log file and position transaction sent to the queue. 
        """
        try:
            self._conn.hmset(self._service_id, {"log_file": log_file, "log_pos": log_pos})
        except Exception as e:
            sys.exit(e) 
