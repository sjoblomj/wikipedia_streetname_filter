#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import calendar
import time


def write_to_file(file_name, string, mode="a"):
    with open(file_name, mode) as outfile:
        outfile.write(string)
        outfile.write("\n")


def file_exists(file_name):
    return os.path.isfile(file_name)


def file_is_older_than_one_day(file_name):
    one_day = 60 * 60 * 24
    return (calendar.timegm(time.gmtime()) - int(os.path.getmtime(file_name))) > one_day


def open_json_file(filename):
    with open(filename) as json_file:
        return json.load(json_file)


def read_json_string(string):
    return json.loads(string)
