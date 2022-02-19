import datetime


def tact_to_data(tact):
    return (datetime.datetime.min + datetime.timedelta(seconds=tact/10000000)).strftime("%d/%m/%Y %H:%M:%S")


def data_to_tact(data):
    difference = data - datetime.datetime.min
    return int(difference.total_seconds()*10000000)
