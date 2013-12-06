#!/usr/bin/python
# -*- coding: utf8 -*-

import sys


def about():
    print "####################################################"
    print "#	@author		Florian Pradines	   #"
    print "#	@company	Phonesec		   #"
    print "#	@mail		f.pradines@phonesec.com	   #"
    print "#	@mail		florian.pradines@owasp.org #"
    print "#	@version	2.0			   #"
    print "#	@licence	GNU GPL v3		   #"
    print "#	@dateCreation	27/03/2013		   #"
    print "#	@lastModified	12/09/2013		   #"
    print "####################################################"
    print ""
    print "Androick will help you in your forensics analysis on android."
    print "put the package name in argument of the application, and the program will download automatically all datas and apk file stored in your android device."
    print "furthermore, after downloading datas, the application will search and extract all databases in CSV format."

    print "####################################################"
    print "# Integrated decompiling feature by Haotian Sun #"
    print "####################################################"

def help():
    print "Usage : " + sys.argv[0] + " [OPTIONS] PACKAGE_NAME_1 [PACKAGE_NAME_2 etc...]"
    print "-a --about : more informations about this program"
    print "-h --help : display this message"
    print "-d --device : serial number of the device"
    print "-f --find : find a package"
    print "-s --src : decompile apk into java source with jad or jd-gui (please specify)"

def printVerbose(process):
    stdout, stderr = process.communicate()
    if stdout != None:
        print stdout
    if stderr != None:
        print stderr
