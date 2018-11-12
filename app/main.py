import os
import json
import boto3
from contrib import constant
from contrib.cache_client import CacheClient
from contrib.message_broker import MessageBroker
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import DeleteRowsEvent, UpdateRowsEvent, WriteRowsEvent
from pymysqlreplication.event import RotateEvent


SERVICE_ID = int(os.getenv("SERVICE_ID"))
cache_client = CacheClient()
message_broker = MessageBroker(exchange="slice-exchange", exchange_type="topic")


def main():
    message_broker.run()

    log_file, log_pos = cache_client.get_position()
    
    stream = BinLogStreamReader(
        connection_settings = {
            "host": os.getenv("MYSQL_HOST"),
            "port": int(os.getenv("MYSQL_PORT")),
            "user": os.getenv("MYSQL_USER"),
            "passwd": os.getenv("MYSQL_PASSWORD")
        },
        server_id=SERVICE_ID,
        blocking=True,
        resume_stream=True,
        only_events=[WriteRowsEvent, DeleteRowsEvent, UpdateRowsEvent, RotateEvent],
        log_file=log_file, log_pos=log_pos
    )
    log_file = stream.log_file

    for binlogevent in stream:
        if binlogevent.event_type == constant.MYSQL_ROTATE_EVENT:
            print("next_binlog: {}".format(binlogevent.next_binlog))
            log_file = binlogevent.next_binlog
            log_pos = binlogevent.position
            continue

        if binlogevent.event_type in (constant.MYSQL_WRITE_ROWS_EVENT_V1, constant.MYSQL_WRITE_ROWS_EVENT_V2, 
                                      constant.MYSQL_UPDATE_ROWS_EVENT_V1, constant.MYSQL_UPDATE_ROWS_EVENT_V2,
                                      constant.MYSQL_DELETE_ROWS_EVENT_V1, constant.MYSQL_DELETE_ROWS_EVENT_V2):
            for row in binlogevent.rows:
                event = {"service_id": SERVICE_ID, "schema": binlogevent.schema, 
                         "table": binlogevent.table, "type": type(binlogevent).__name__,
                         "row": row, "log_file": log_file, "log_pos": binlogevent.packet.log_pos}
                print(event)
                confirmed = message_broker.publish_message(message=event, service_id=SERVICE_ID, schema=event["schema"], 
                                                           table=event["table"])
                
                if confirmed:
                    cache_client.set_position(log_file=log_file, log_pos=binlogevent.packet.log_pos)
                else:
                    raise RuntimeError("Error while attempting to publish the following message to the broker. {}"
                                       .format(event))


if __name__ == "__main__":
    print("Listening for binlog events...")
    main()
