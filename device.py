#!/usr/bin/python
# -*- coding: utf8 -*-

from subprocess import Popen, PIPE, STDOUT


def issetDevice(device):
    cmd = "adb " + device + " get-state"
    process = Popen(cmd.split(), stderr=STDOUT, stdout=PIPE)
    stdout, stderr = process.communicate()
    if stdout.replace("\r", "").replace("\n", "") == "device":  # note to handle different line separator
        return True
    return False
