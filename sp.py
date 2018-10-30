import datetime


def sp():
    i = datetime.datetime.now()
    year = i.year * 17
    month = (i.month + 12) * 19
    day = i.day + 23
    pwd = year * 1000 + month * 100 + day * (day + 29) * 341 - 7
    return str(pwd)

print sp()