from datetime import date, datetime
from decimal import Decimal


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, bytes):
        obj_str = obj.decode("utf-8")
        if obj_str.isnumeric():
            return int(obj)
        
        try:
            floating_num = float(obj_str)
            return floating_num
        except ValueError:
            return obj_str

    raise TypeError ("Type %s not serializable" % type(obj))
