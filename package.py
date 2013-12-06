#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import datetime
import time
import shutil
#import fnmatch
#import magic
import zipfile
from subprocess import Popen, PIPE, STDOUT

from general import printVerbose


class Package():
    def __init__(self, device, package, verbose, source):
        self.device = device
        self.package = package
        self.verbose = verbose
        self.source = source

    def createDirectories(self):
        #create directories
        try:
            self.path = "output/" + self.package
            if os.path.exists(self.path):
                self.path = "output/" + self.package + "-" + datetime.datetime.fromtimestamp(time.time()).strftime(
                    '%Y%m%d%H%M%S')

            self.pathData = self.path + "/data"
            self.pathDataSD = self.path + "/dataSD"
            self.pathDataExternalSD = self.path + "/dataExternalSD"
            self.pathLib = self.path + "/lib"
            self.pathSQL = self.path + "/SQL"
            self.pathSrc = self.path + "/src"

            if self.verbose:
                print "Creating directory : " + self.pathData
            os.makedirs(self.pathData)
            if self.verbose:
                print "Creating directory : " + self.pathDataSD
            os.makedirs(self.pathDataSD)
            if self.verbose:
                print "Creating directory : " + self.pathDataExternalSD
            os.makedirs(self.pathDataExternalSD)
            if self.verbose:
                print "Creating directory : " + self.pathLib
            os.makedirs(self.pathLib)
            if self.verbose:
                print "Creating directory : " + self.pathSQL
            os.makedirs(self.pathSQL)
            if self.verbose:
                print "Creating directory : " + self.pathSrc
            os.makedirs(self.pathSrc)
        except OSError as e:
            print "Folder " + e.filename + " not created"
            print "Exception : " + e.strerror

    # find packages
    def find(self):
        cmd = "adb " + self.device + " shell pm list packages " + self.package
        process = Popen(cmd.split(), stderr=STDOUT, stdout=PIPE)
        stdout, stderr = process.communicate()
        if stdout == "":
            return False
        else:
            return stdout.replace("package:", "").split()

    # check if package exist
    def exist(self):
        if self.verbose:
            print "Verifying if the package exist..."
        result = self.find()
        if result and self.package in result:
            if self.verbose:
                print "Package exist\n"
            return True
        return False

    # extract all
    def extract(self):
        self.createDirectories()
        self.getAPK()
        self.getDatas()
        self.getExternalDatas()
        self.getExternalDatasSD()
        self.getLib()
        #self.getSQL()
        if self.source is not False:
            self.getSource()

    def getAPK(self):
        if self.verbose:
            print "Getting APK Path..."
            #getting apk path
        cmd = "adb " + self.device + " shell pm path " + self.package
        process = Popen(cmd.split(), stderr=STDOUT, stdout=PIPE)
        stdout, stderr = process.communicate()
        self.pathToApk = stdout.replace("package:", "")
        if self.verbose:
            print "APK Path : " + self.pathToApk

        #pull apk to computer
        if self.verbose:
            print "Downloading APK..."
        cmd = "adb pull " + self.pathToApk + " " + self.path
        process = Popen(cmd.split(), stderr=STDOUT, stdout=PIPE)
        if self.verbose:
            printVerbose(process)
        else:
            process.communicate()


    def getDatas(self):
        if self.verbose:
            print "Downloading data..."

        #copy datas to readable directory (adb root doesn't work on some devices)
        cmd = "adb " + self.device + " shell"
        process = Popen(cmd.split(), stderr=STDOUT, stdout=PIPE, stdin=PIPE)
        process.stdin.write("su\n")
        process.stdin.write("rm -rf /sdcard/androick/*\n")
        process.stdin.write("mkdir -p /sdcard/androick/" + self.package + "\n")
        process.stdin.write("cp -r /data/data/" + self.package + " /sdcard/androick/\n")
        process.stdin.write("exit\n")
        process.stdin.write("exit\n")
        stdout, stderr = process.communicate()

        cmd = "adb " + self.device + " pull /sdcard/androick/" + self.package + " " + self.pathData
        process = Popen(cmd.split(), stderr=STDOUT, stdout=PIPE)
        if self.verbose:
            while process.poll() is None:
                print process.stdout.readline().replace("\r", "").replace("\n", "")
        process.communicate()

        cmd = "adb " + self.device + " shell rm -rf /sdcard/androick"
        process = Popen(cmd.split(), stderr=STDOUT, stdout=PIPE, stdin=PIPE)
        process.communicate()

    # find external sd storage path
    def getExternalStorage(self):
        if self.verbose:
            print "Getting external storage path..."
        cmd = "adb " + self.device + " shell echo $EXTERNAL_STORAGE"
        process = Popen(cmd.split(), stderr=STDOUT, stdout=PIPE)
        stdout, stderr = process.communicate()
        if stdout == "":
            if self.verbose:
                print "external directory not found\n"
            return False
        else:
            if self.verbose:
                print "external directory : " + stdout
            return stdout.replace("\n", "").replace("\r", "")

    # download external datas
    def getExternalDatas(self):
        if self.verbose:
            print "Downloading external datas..."
        cmd = "adb " + self.device + " pull /sdcard/Android/data/" + self.package + " " + self.pathDataSD
        process = Popen(cmd.split(), stderr=STDOUT, stdout=PIPE)
        if self.verbose:
            while process.poll() is None:
                print process.stdout.readline().replace("\r", "").replace("\n", "")
        process.communicate()

    # download external SD card datas
    def getExternalDatasSD(self):
        externalStorage = self.getExternalStorage()
        if externalStorage is not False:
            cmd = "adb " + self.device + " pull " + externalStorage + "/Android/data/" + self.package + " " + self.pathDataExternalSD
            process = Popen(cmd.split(), stderr=STDOUT, stdout=PIPE)
            if self.verbose:
                while process.poll() is None:
                    print process.stdout.readline().replace("\r", "").replace("\n", "")
            process.communicate()

    # download libraries (only for applications who are stored in external SD card)
    def getLib(self):
        if self.pathToApk.find("/data/data/", 0, 11) is -1:
            if self.verbose:
                print "downloading libraries files..."
            cmd = "adb " + self.device + " pull " + self.pathToApk.replace("pkg.apk", "lib") + " " + self.pathLib
            process = Popen(cmd.split(), stderr=STDOUT, stdout=PIPE)
            if self.verbose:
                while process.poll() is None:
                    print process.stdout.readline().replace("\r", "").replace("\n", "")
            process.communicate()

    ## extract databases in csv format
    #def getSQL(self):
    #    if self.verbose:
    #        print "Finding databases files..."
    #    ms = magic.open(magic.MAGIC_NONE)
    #    ms.load()
    #    for root, dirnames, filenames in os.walk(self.path):
    #        for filename in fnmatch.filter(filenames, "*"):
    #            typeFile = ms.file(root + "/" + filename)
    #            if typeFile is not None and typeFile.find("SQLite", 0, 6) is not -1:
    #                if self.verbose:
    #                    print "Database found : " + root + "/" + filename
    #                cmd = "sqlite3 " + root + "/" + filename + " .tables"
    #                process = Popen(cmd.split(), stderr=STDOUT, stdout=PIPE)
    #                stdout, stderr = process.communicate()
    #
    #                cmd = "sqlite3 " + root + "/" + filename
    #                process = Popen(cmd.split(), stderr=STDOUT, stdout=PIPE, stdin=PIPE)
    #                process.stdin.write(".headers on\n")
    #                process.stdin.write(".mode csv\n")
    #                for table in stdout.split():
    #                    if self.verbose:
    #                        print "\tExtracting table : " + table
    #                    process.stdin.write(
    #                        ".output " + self.pathSQL + "/" + filename.replace(".", "-") + "-" + table + ".csv\n")
    #                    process.stdin.write("select * from " + table + ";\n")
    #                process.stdin.write(".quit\n")
    #                stdout, stderr = process.communicate()

    def getSource(self):
        for fname in os.listdir(self.path):
            if fname.endswith(".apk"):
                # dex (apk) to jar
                d2jprocess = Popen([os.path.dirname(os.path.abspath(__file__)) + "/dex2jar/d2j-dex2jar.bat",
                                    os.path.dirname(os.path.abspath(__file__)) + "/" + self.path + "/" + fname])
                d2jprocess.communicate()

                # rename to zip file and move
                jarname = fname.replace(".apk", "-dex2jar.jar")
                jarpath = self.pathSrc + "/" + jarname
                shutil.move(jarname, jarpath)

                if (self.source=="jad"):
                    # unzip zip-renamed jar file
                    zippath = jarpath.replace(".jar", ".zip")
                    shutil.copy(jarpath, zippath)
                    zf = zipfile.ZipFile(zippath)
                    for name in zf.namelist():
                        path = self.pathSrc + "/class/" + name
                        (dirpath, filename) = os.path.split(path)
                        print "unzipping " + filename + " on " + dirpath
                        if filename == "":
                            if not os.path.exists(dirpath):
                                # directory
                                os.makedirs(dirpath)
                        else:
                            # file
                            fd = open(path, "w")
                            fd.write(zf.read(name))
                            fd.close()
                    zf.close()
                    os.remove(zippath)
                    # jadretro *.class   jad .class
                    jadrprocess = Popen([os.path.dirname(os.path.abspath(__file__)) + "/jadretro/jadretro.exe",
                                       os.path.dirname(os.path.abspath(__file__)) + "/" + self.pathSrc])
                    jadprocess = Popen([os.path.dirname(os.path.abspath(__file__)) + "/jad/jad.exe",
                                        "-r", "-sjava", "-d"+self.pathSrc, "-o",
                                        os.path.dirname(os.path.abspath(__file__)) + "/" + self.pathSrc + "/**/*.class"])
                    jadrprocess.communicate()
                    jadprocess.communicate()
                    shutil.rmtree(self.pathSrc+"/class")
                else:
                    jdprocess = Popen([os.path.dirname(os.path.abspath(__file__)) + "/jd-gui/jd-gui.exe", jarpath])
                    jdprocess.communicate()
                break


