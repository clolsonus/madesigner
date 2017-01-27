#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
MA creator 

This program hopefully does something eventually ...

author: Curtis L. Olson
website: madesigner.flightgear.org
started edited: November 2013
"""

import sys
import os.path
import time
import subprocess
import distutils.spawn
import urllib2
from PyQt4 import QtGui, QtCore

from props import PropertyNode
import props_xml
import props_json

from overview import Overview
from wing_ui import WingUI
from builder import Builder
from version import MADversion


# Check if our version is the latest
class CheckVersion(QtCore.QThread):

    def __init__(self):
        super(CheckVersion, self).__init__()
        self.version = MADversion()
        self.baseurl = "http://mirrors.ibiblio.org/flightgear/ftp/MAdesigner"
        self.file = "stable_version"

    def run(self):
        time.sleep(2)
        #print "Checking for newer version.  We are " + str(self.version)
        try:
            url = self.baseurl + "/" + self.file
            response = urllib2.urlopen(url)
            html = response.read()
            stable_version = float(html)
            #print str(stable_version)
            if self.version.get() < stable_version:
                self.emit( QtCore.SIGNAL('update(QString)'),
                           str(stable_version) )
        except:
            # print "version check error = " + str(sys.exc_info()[1])
            # do nothing
            a = 1

        return


class CreatorUI(QtGui.QWidget):
    
    def __init__(self, filename=""):
        super(CreatorUI, self).__init__()
        self.default_title = "Model Aircraft Creator"
        self.wings = []
        self.initUI()
        self.filename = ""
        self.fileroot = ""
        self.load(filename)
        self.clean = True

        # version checking task
        self.checkversion = CheckVersion()
        self.connect( self.checkversion, QtCore.SIGNAL("update(QString)"),
                      self.version_message )
        self.checkversion.start()

    def version_message(self, text):
        reply = QtGui.QMessageBox.question(self, 'Version Check', 'A new version of MAdesigner (v' + text + ') is available.<br><a href="http://mirrors.ibiblio.org/flightgear/ftp/MAdesigner">Click here to download it.</A>', QtGui.QMessageBox.Ok)

    def onChange(self):
        #print "parent onChange() called!"
        result = self.rebuildTabNames()
        if result:
            self.rebuildWingLists()
        self.clean = False

    def isClean(self):
        return self.clean

    def setClean(self):
        self.clean = True

    def rebuildTabNames(self):
        updated = False
        i = 0
        for wing in self.wings:
            if wing.valid:
                wing_name = "Wing: " + wing.get_name()
                tab_name = self.tabs.tabText(i+1)
                if wing_name != tab_name:
                    self.tabs.setTabText(i+1, wing_name)
                    updated = True
                i += 1
        return updated

    def rebuildWingLists(self):
        wing_names = []
        for wing in self.wings:
            if wing.valid:
                wing_names.append(wing.get_name())
        for wing in self.wings:
            if wing.valid:
                wing.rebuild_wing_list( wing_names )

    def initUI(self):               
        self.setWindowTitle( self.default_title )

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        # 'File' button bar
        file_group = QtGui.QFrame()
        layout.addWidget(file_group)
        file_layout = QtGui.QHBoxLayout()
        file_group.setLayout( file_layout )

        new = QtGui.QPushButton('New')
        new.clicked.connect(self.new_design)
        file_layout.addWidget(new)

        open = QtGui.QPushButton('Open...')
        open.clicked.connect(self.open_home)
        file_layout.addWidget(open)

        open = QtGui.QPushButton('Open Examples...')
        open.clicked.connect(self.open_examples)
        file_layout.addWidget(open)

        save = QtGui.QPushButton('Save')
        save.clicked.connect(self.save)
        file_layout.addWidget(save)

        saveas = QtGui.QPushButton('Save As...')
        saveas.clicked.connect(self.saveas)
        file_layout.addWidget(saveas)

        quit = QtGui.QPushButton('Quit')
        quit.clicked.connect(self.quit)
        file_layout.addWidget(quit)

        file_layout.addStretch(1)

        # Main work area
        self.tabs = QtGui.QTabWidget()
        layout.addWidget( self.tabs )

        self.overview = Overview(changefunc=self.onChange)
        self.tabs.addTab( self.overview.get_widget(), "Overview" );

        # 'Command' button bar
        cmd_group = QtGui.QFrame()
        layout.addWidget(cmd_group)
        cmd_layout = QtGui.QHBoxLayout()
        cmd_group.setLayout( cmd_layout )

        cmd_layout.addWidget( QtGui.QLabel("<b>Design Tools:</b> ") )

        add_wing = QtGui.QPushButton('Add Wing...')
        add_wing.clicked.connect(self.add_wing)
        cmd_layout.addWidget(add_wing)
  
        #add_fuse = QtGui.QPushButton('Add Fuselage...')
        #add_fuse.clicked.connect(self.add_fuse)
        #cmd_layout.addWidget(add_fuse)
  
        fast_build = QtGui.QPushButton('Fast Build...')
        fast_build.clicked.connect(self.build_fast)
        cmd_layout.addWidget(fast_build)
  
        detail_build = QtGui.QPushButton('Detail Build...')
        detail_build.clicked.connect(self.build_detail)
        cmd_layout.addWidget(detail_build)
  
        view3d = QtGui.QPushButton('View 3D')
        view3d.clicked.connect(self.view3d)
        cmd_layout.addWidget(view3d)
  
        cmd_layout.addStretch(1)

        self.resize(800, 700)
        self.show()

    def add_wing(self):
        self.onChange()
        valid_wing_count = 0
        for wing in self.wings:
            if wing.valid:
                valid_wing_count += 1
        name = str( valid_wing_count + 1 )
        wing = WingUI(changefunc=self.onChange, name=name)
        self.wings.append(wing)
        self.tabs.addTab( wing.get_widget(), "Wing: " + name )

    #def add_fuse(self):
    #    print "add fuse requested"

    def build_fast(self):
        if not self.isClean():
            reply = QtGui.QMessageBox.question(self, "The design has been modified.", "You must save before a build.", QtGui.QMessageBox.Save | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Save)
            if reply == QtGui.QMessageBox.Save:
                self.save()
            elif reply == QtGui.QMessageBox.Cancel:
                return

        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        build = Builder(filename=self.filename, airfoil_resample=25,
                        circle_points=8, nest_speed="fast")
        QtGui.QApplication.restoreOverrideCursor()

    def build_detail(self):
        if not self.isClean():
            reply = QtGui.QMessageBox.question(self, "The design has been modified.", "You must save before a build.", QtGui.QMessageBox.Save | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Save)
            if reply == QtGui.QMessageBox.Save:
                self.save()
            elif reply == QtGui.QMessageBox.Cancel:
                return

        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        build = Builder(filename=self.filename, airfoil_resample=1000,
                        circle_points=32, nest_speed="nice")
        QtGui.QApplication.restoreOverrideCursor()

    def view3d(self):
        viewer = "osgviewer"

        # look for viewer in the standard path
        result = distutils.spawn.find_executable(viewer)

        if result == None:
            app_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
            viewer = os.path.abspath(app_path + "/OpenSceneGraph/bin/osgviewer")
            viewerexe = os.path.abspath(app_path + "/OpenSceneGraph/bin/osgviewer.exe")
            print "testing for " + viewer + " or " + viewerexe
            result = os.path.isfile(viewer) or os.path.isfile(viewerexe)

        if not result:
            error = QtGui.QErrorMessage(self)
            error.showMessage( "Cannot find " + viewer + " in path.  Perhaps it needs to be installed?" )
            return
            
        madfile = self.fileroot + ".mad"
        if not os.path.exists(madfile):
            error = QtGui.QErrorMessage(self)
            error.showMessage( "No '.mad' file ... please save your design with a file name." )
            return 

        if not self.isClean():
            error = QtGui.QErrorMessage(self)
            error.showMessage( "The design has been modified.  You must <b>Build</b> it before viewing the 3d structure." )
            return 

        acfile = self.fileroot + ".ac"
        if not os.path.exists(acfile):
            error = QtGui.QErrorMessage(self)
            error.showMessage( "Design needs to be 'built'; click ok to continue." )
            #self.build_fast()
            return

        madtime = os.path.getmtime(madfile)
        actime = os.path.getmtime(acfile)
        if madtime > actime:
            error = QtGui.QErrorMessage(self)
            error.showMessage( "Design needs to be 'built'; click ok to continue." )
            #self.build_fast()
            return

        command = []
        command.append(viewer)
        command.append("--window")
        command.append("50")
        command.append("50")
        command.append("800")
        command.append("600")
        command.append(self.fileroot + ".ac")
        pid = subprocess.Popen(command).pid
        print "spawned osgviewer with pid = " + str(pid)
 
    def wipe_slate(self):
        self.overview.wipe_clean()
        for wing in self.wings:
            wing.delete_self()
        self.clean = True

    def load(self, filename):
        if filename == "":
            # new empty design
            return

        basename = os.path.basename(str(filename))
        fileroot, ext = os.path.splitext(basename)

        if not os.path.exists(filename):
            # invalid/nonexistent filename
            return

        self.wipe_slate()

        design = PropertyNode()
        if props_json.load(filename, design):
            print "json format: successful"
        elif props_xml.load(filename, design):
            print "xml format: successful"
        else:
            error = QtGui.QErrorMessage(self)
            error.showMessage( filename + ": load failed" )
            return
        # design.pretty_print()

        self.setWindowTitle( self.default_title + " - " + fileroot )

        self.filename = str(filename)
        self.fileroot, ext = os.path.splitext(self.filename)

        node = design.getChild('overview', True)
        self.overview.load(node)

        design.setLen('wing', 1) # force to be enumerated if not already
        num_wings = design.getLen('wing')
        for i in range(num_wings):
            wing_node = design.getChild('wing[%d]' % i)
            wing = WingUI(changefunc=self.onChange)
            wing.load(wing_node)
            self.wings.append(wing)
            self.tabs.addTab( wing.get_widget(), "Wing: " + wing.get_name() )
        self.rebuildWingLists()

    def new_design(self):
        # wipe the current design (by command or before loading a new design)
        if not self.isClean():
            reply = QtGui.QMessageBox.question(self, "The design has been modified.", "Do you want to save your changes?", QtGui.QMessageBox.Save | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Save)
            #print "response = " + str(reply)
            if reply == QtGui.QMessageBox.Save:
                self.save()
            elif reply == QtGui.QMessageBox.Cancel:
                return

        self.wipe_slate()

    def open(self, startdir=None):
        if not self.isClean():
            reply = QtGui.QMessageBox.question(self, "The design has been modified.", "Do you want to save your changes?", QtGui.QMessageBox.Save | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Save)
            #print "response = " + str(reply)
            if reply == QtGui.QMessageBox.Save:
                self.save()
            elif reply == QtGui.QMessageBox.Cancel:
                return

        if startdir == None:
            startdir = os.path.expanduser("~")
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                                                     startdir,
                                                     "MAdesigner (*.mad)")
        if ( filename == "" ):
            return
        self.load(str(filename))

    def open_home(self):
        startdir = os.path.expanduser("~")
        self.open(startdir)

    def open_examples(self):
        app_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
        startdir = os.path.abspath(app_path + "/examples")
        self.open(startdir)

    def setFileName(self):
        startdir = os.path.expanduser("~/newdesign.mad")
        return QtGui.QFileDialog.getSaveFileName(self, "Save File",
                                                 startdir,
                                                 "MAdesigner (*.mad)")

    def save(self):
        if self.filename == "":
            filename = str(self.setFileName())
            if filename == "":
                # print "cancelled save ..."
                return
            else:
                self.filename = filename
                self.fileroot, ext = os.path.splitext(self.filename)
                # print self.fileroot, ext

        # create a new design root
        design = PropertyNode()

        # overview
        node = design.getChild('overview', True)
        self.overview.save(node)

        # wings
        i = 0
        for wing in self.wings:
            if wing.valid:
                node = design.getChild('wing[%d]' % i, True)
                wing.save(node)
                i += 1

        try:
            props_json.save(self.filename, design)
        except:
            print "error saving file"
            return

        self.setWindowTitle( self.default_title + " - " + os.path.basename(str(self.filename)) )
        self.setClean()

    def saveas(self):
        filename = self.setFileName()

        if filename == "":
            # print "cancelled save as ..."
            return
        else:
            self.filename = str(filename)
            self.fileroot, ext = os.path.splitext(self.filename)

        self.save()

    def quit(self):
        if not self.isClean():
            reply = QtGui.QMessageBox.question(self, "The design has been modified.", "Do you want to save your changes?", QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Save)
            #print "response = " + str(reply)
            if reply == QtGui.QMessageBox.Save:
                self.save()
            elif reply == QtGui.QMessageBox.Cancel:
                return

        QtCore.QCoreApplication.instance().quit()
