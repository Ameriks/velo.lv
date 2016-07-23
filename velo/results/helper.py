import datetime


def time_to_seconds(time):
    return (datetime.datetime.combine(datetime.datetime.today(), time) - datetime.datetime.combine(datetime.datetime.today(), datetime.time())).total_seconds()


def seconds_to_time(seconds: float) -> datetime.time:
    hours = (seconds - seconds % (60*60)) / (60*60)
    if hours > 23:
        raise Exception("Hours cannot be >23")
    seconds -= hours * 60 * 60
    minutes = (seconds - seconds % 60) / 60
    seconds -= minutes * 60
    return datetime.time(int(hours), int(minutes), int(seconds), int((seconds % 1) * 1000))
