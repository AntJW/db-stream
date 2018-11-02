import os
import json
import boto3
from cache_client import CacheClient
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import DeleteRowsEvent, UpdateRowsEvent, WriteRowsEvent
from pymysqlreplication.event import RotateEvent

cache = CacheClient()

def main():
    log_file, log_pos = cache.get_position()

    stream = BinLogStreamReader(
        connection_settings = {
            "host": os.getenv("MYSQL_HOST"),
            "port": int(os.getenv("MYSQL_PORT")),
            "user": os.getenv("MYSQL_USER"),
            "passwd": os.getenv("MYSQL_PASSWORD")
        },
        server_id=int(os.getenv("SERVICE_ID")),
        blocking=True,
        resume_stream=True,
        only_events=[WriteRowsEvent, DeleteRowsEvent, UpdateRowsEvent, RotateEvent],
        log_file=log_file, log_pos=log_pos
    )
    log_file = stream.log_file

    for binlogevent in stream:
        if binlogevent.event_type == 4:
            print("next_binlog: {}".format(binlogevent.next_binlog))
            log_file = binlogevent.next_binlog
            continue

        for row in binlogevent.rows:
            event = {"schema": binlogevent.schema, "table": binlogevent.table, "type": type(binlogevent).__name__,
                     "row": row, "log_file": log_file, "log_pos": binlogevent.packet.log_pos}

            print(event)

            cache.set_position(log_file=log_file, log_pos=binlogevent.packet.log_pos)


if __name__ == "__main__":
    print("Listening for binlog events...")
    main()
