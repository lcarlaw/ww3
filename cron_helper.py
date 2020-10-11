from datetime import datetime

def timestamp(str1, str2):
    """Print out some simple date and time information for log files
    """
    print("%s  %s : %s" % (str1, datetime.strftime(datetime.now(), "%c"), str2))
