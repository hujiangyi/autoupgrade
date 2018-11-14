#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
cmdfile = open('./collectDataCmd.txt', "r")
for line in cmdfile.readlines():
    print line.strip()