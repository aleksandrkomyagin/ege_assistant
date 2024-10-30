import logging
import pytz
from datetime import datetime


class CustomFormatter(logging.Formatter):
    def converter(self, timestamp):
        tz = pytz.timezone('Europe/Moscow')
        dt = datetime.fromtimestamp(timestamp, tz)
        return dt.timetuple()
