import datetime


# Get date and time for loggin timestamp.
def get_timestamp():
    timestamp = str(datetime.datetime.now())
    timestamp = timestamp.replace(' ', '_')
    timestamp = timestamp.replace(':', '-')
    timestamp = timestamp.replace('.', '-')
    return timestamp
