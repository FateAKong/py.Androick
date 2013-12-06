#!/usr/bin/python
# -*- coding: utf8 -*-

#<Androick - OWASP Android Project : Forensic analysis helper>
#Copyright (C) <2013>  <Florian Pradines>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import getopt

from general import *
from device import *
from package import *


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ahvd:f:s:", ["about", "help", "verbose", "device=", "find=", "src="])
    except getopt.GetoptError, err:
        print err
        help()
        sys.exit(2)

    device = ""
    find = False
    verbose = False
    src = False

    #Parse options
    for opt, arg in opts:
        if opt in ("-a", "--about"):
            about()
            sys.exit()
        if opt in ("-h", "--help"):
            help()
            sys.exit()
        if opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-d", "--device"):
            device = "-s " + arg
        elif opt in ("-f", "--find"):
            find = arg
        elif opt in ("-s", "--src"):
            src = arg

    if (len(args) == 0 and find == False) or (src is not False and src != "jad" and src != "jd-gui"):
        help()
        sys.exit(2)

    #start adb server
    if verbose == True:
        print "Starting adb server..."
    process = Popen(["adb", "start-server"], stderr=STDOUT, stdout=PIPE)
    if verbose:
        printVerbose(process)
    else:
        process.communicate()

    #validate given device (if given)
    if device != "" and issetDevice(device) is False:
        print "Device not found"
        sys.exit(2)

    #find package if asked
    if find:
        package = Package(device, find, verbose, src)
        result = package.find()
        if result is False:
            print "no packages found with this name"
            sys.exit()
        else:
            print "packages found with this name : "
            i = 1
            for package in result:
                print str(i) + ") " + package
                i += 1

            choices = raw_input("Which packages do you want extract. Ex: 1 3 6 (type 0 to quit) : ").split()
            if choices[0] is "0":
                sys.exit(0)

            args = []
            for choice in map(int, choices):
                if choice < 1 or choice > len(result):
                    print str(choice) + " is not a good value"
                else:
                    args.append(result[choice - 1])

    #parse & extract packages
    for arg in args:
        package = Package(device, arg, verbose, src)
        if package.exist():
            package.extract()
        else:
            print "Package " + arg + " not found"


if __name__ == "__main__":
    main()
