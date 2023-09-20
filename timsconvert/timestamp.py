import datetime


def get_timestamp():
    """
    Get timestamp in ISO 8601 format.

    :return: ISO 8601 format timestamp.
    :rtype: str
    """
    return datetime.datetime.now().isoformat()
