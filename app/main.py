import json
import boto3

from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import DeleteRowsEvent, UpdateRowsEvent, WriteRowsEvent
from pymysqlreplication.event import RotateEvent


def main():
    stream = BinLogStreamReader(
        connection_settings = {
            "host": "",
            "port": 3306,
            "user": "",
            "passwd": ""
        },
        server_id=1,
        blocking=True,
        resume_stream=True,
        only_events=[WriteRowsEvent, DeleteRowsEvent, UpdateRowsEvent, RotateEvent],
        log_file="mysql-bin-changelog.000261", log_pos=55980698
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


if __name__ == "__main__":
    print("Listening for binlog events...")
    main()
