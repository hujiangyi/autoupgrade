#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
import datetime


def sp():
    i = datetime.datetime.now()
    year = i.year * 17
    month = (i.month + 12) * 19
    day = i.day + 23
    pwd = year * 1000 + month * 100 + day * (day + 29) * 341 - 7
    return str(pwd)

print sp()