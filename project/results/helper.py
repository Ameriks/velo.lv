import datetime


def time_to_seconds(time):
    return (datetime.datetime.combine(datetime.datetime.today(), time) - datetime.datetime.combine(datetime.datetime.today(), datetime.time())).total_seconds()