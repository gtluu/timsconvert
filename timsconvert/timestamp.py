import datetime


def get_iso8601_timestamp():
    """
    Get timestamp in ISO 8601 format.

    :return: ISO 8601 format timestamp.
    :rtype: str
    """
    return datetime.datetime.now().isoformat()


def get_timestamp():
    """
    Get timestamp in non-standard format that is compatible with Windows file system.

    :return: Timestamp.
    :rtype: str
    """
    timestamp = str(datetime.datetime.now())
    timestamp = timestamp.replace(' ', '_')
    timestamp = timestamp.replace(':', '-')
    timestamp = timestamp.replace('.', '-')
    return timestamp
