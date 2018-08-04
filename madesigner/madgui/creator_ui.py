# creator_ui.py - main creator window components
#
# Copyright (C) 2013-2017 - Curtis Olson, curtolson@flightgear.org
# http://madesigner.flightgear.org

import sys
import os.path
import time
import subprocess
import distutils.spawn
from pkg_resources import resource_listdir, resource_stream
import urllib2

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QWidget,
                             QHBoxLayout, QVBoxLayout, QFrame, QFormLayout,
                             QPushButton, QTabWidget, QGroupBox,
                             QLineEdit, QTextEdit, QLabel, QScrollArea,
                             QInputDialog, QMenu, QMessageBox,
                             QFileDialog, QErrorMessage)
from PyQt5.QtGui import QCursor

from props import PropertyNode
import props_xml
import props_json

from overview import Overview
from wing_ui import WingUI
from version import MADversion

from madlib.builder import Builder

# test for writeable path
import tempfile
import errno
def isWritable(path):
    try:
        testfile = tempfile.TemporaryFile(dir=path)
        testfile.close()
    except OSError as e:
        if e.errno == errno.EACCES:  # 13
            return False
        e.filename = path
        raise
    return True

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


class CreatorUI(QWidget):
    
    def __init__(self, filename=""):
        super(CreatorUI, self).__init__()
        self.default_title = "Model Aircraft Creator"
        self.wings = []
        self.initUI()
        self.filename = ""
        self.fileroot = ""
        self.load(filename)
        self.clean = True
        self.dirname = "."

        # version checking task (fixme)
        # self.checkversion = CheckVersion()
        # self.connect( self.checkversion, QtCore.SIGNAL("update(QString)"),
        #               self.version_message )
        # self.checkversion.start()

    def version_message(self, text):
        reply = QMessageBox.question(self, 'Version Check', 'A new version of MAdesigner (v' + text + ') is available.<br><a href="http://mirrors.ibiblio.org/flightgear/ftp/MAdesigner">Click here to download it.</A>', QMessageBox.Ok)

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

        layout = QVBoxLayout()
        self.setLayout(layout)

        # 'File' button bar
        file_group = QFrame()
        layout.addWidget(file_group)
        file_layout = QHBoxLayout()
        file_group.setLayout( file_layout )

        new = QPushButton('New')
        new.clicked.connect(self.new_design)
        file_layout.addWidget(new)

        open = QPushButton('Open...')
        open.clicked.connect(self.open_home)
        file_layout.addWidget(open)

        open = QPushButton('Load Example...')
        open.clicked.connect(self.load_example)
        file_layout.addWidget(open)

        save = QPushButton('Save')
        save.clicked.connect(self.save)
        file_layout.addWidget(save)

        saveas = QPushButton('Save As...')
        saveas.clicked.connect(self.saveas)
        file_layout.addWidget(saveas)

        quit = QPushButton('Quit')
        quit.clicked.connect(self.quit)
        file_layout.addWidget(quit)

        file_layout.addStretch(1)

        # Main work area
        self.tabs = QTabWidget()
        layout.addWidget( self.tabs )

        self.overview = Overview(changefunc=self.onChange)
        self.tabs.addTab( self.overview.get_widget(), "Overview" );

        # 'Command' button bar
        cmd_group = QFrame()
        layout.addWidget(cmd_group)
        cmd_layout = QHBoxLayout()
        cmd_group.setLayout( cmd_layout )

        cmd_layout.addWidget( QLabel("<b>Design Tools:</b> ") )

        add_wing = QPushButton('Add Wing...')
        add_wing.clicked.connect(self.add_wing)
        cmd_layout.addWidget(add_wing)
  
        #add_fuse = QPushButton('Add Fuselage...')
        #add_fuse.clicked.connect(self.add_fuse)
        #cmd_layout.addWidget(add_fuse)
  
        fast_build = QPushButton('Fast Build...')
        fast_build.clicked.connect(self.build_fast)
        cmd_layout.addWidget(fast_build)
  
        detail_build = QPushButton('Detail Build...')
        detail_build.clicked.connect(self.build_detail)
        cmd_layout.addWidget(detail_build)
  
        view3d = QPushButton('View 3D')
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
            reply = QMessageBox.question(self, "The design has been modified.", "You must save before a build.", QMessageBox.Save | QMessageBox.Cancel, QMessageBox.Save)
            if reply == QMessageBox.Save:
                self.save()
            elif reply == QMessageBox.Cancel:
                return

        QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
        design = self.gen_property_tree()

        dir,_ = os.path.split(self.filename)

        build = Builder(design, dirname=dir + os.sep , airfoil_resample=25,
                        circle_points=8, nest_speed="fast")
        QApplication.restoreOverrideCursor()

    def build_detail(self):
        if not self.isClean():
            reply = QMessageBox.question(self, "The design has been modified.", "You must save before a build.", QMessageBox.Save | QMessageBox.Cancel, QMessageBox.Save)
            if reply == QMessageBox.Save:
                self.save()
            elif reply == QMessageBox.Cancel:
                return

        QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
        design = self.gen_property_tree()

        dir, _ = os.path.split(self.filename)
        build = Builder(design, dirname=dir + os.sep, airfoil_resample=1000,
                        circle_points=32, nest_speed="nice")
        QApplication.restoreOverrideCursor()

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
            error = QErrorMessage(self)
            error.showMessage( "Cannot find " + viewer + " in path.  Perhaps it needs to be installed?" )
            return
            
        madfile = self.fileroot + ".mad"
        if not os.path.exists(madfile):
            error = QErrorMessage(self)
            error.showMessage( "No '.mad' file ... please save your design with a file name." )
            return 

        if not self.isClean():
            error = QErrorMessage(self)
            error.showMessage( "The design has been modified.  You must <b>Build</b> it before viewing the 3d structure." )
            return 

        acfile = self.fileroot + ".ac"
        if not os.path.exists(acfile):
            error = QErrorMessage(self)
            error.showMessage( "Design needs to be 'built'; click ok to continue." )
            #self.build_fast()
            return

        madtime = os.path.getmtime(madfile)
        actime = os.path.getmtime(acfile)
        if madtime > actime:
            error = QErrorMessage(self)
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
        self.setClean()

    # load from a filename
    def load(self, filename):
        if filename == "":
            # new empty design
            return
        
        self.dirname = os.path.split(os.path.realpath(filename))[0]
        if not isWritable(self.dirname):
            QMessageBox.question(self, 'Directory Access Notice', 'The directory <b>' + self.dirname + '</b> is not writable.  Using <b>' + os.getcwd() + '</b> to save build files.', QMessageBox.Ok)
            self.dirname = os.getcwd()
            
                                     
        basename = os.path.basename(str(filename))
        fileroot, ext = os.path.splitext(basename)
        print filename
        
        if not os.path.exists(filename):
            # invalid/nonexistent filename
            print "invalid file name"
            return

        self.filename = str(filename)
        self.fileroot, ext = os.path.splitext(self.filename)

        f = open(filename, 'r')
        stream = f.read()
        f.close()

        self.loads(stream, fileroot)

    # load from a stream (string)
    def loads(self, stream, fileroot):
        self.wipe_slate()

        design = PropertyNode()
        if props_json.loads(stream, design, ""):
            print "json parse successful"
        else:
            error = QErrorMessage(self)
            error.showMessage( "json parse failed" )
            return False
        # design.pretty_print()

        self.setWindowTitle( self.default_title + " - " + fileroot )

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
        self.setClean()

    def new_design(self):
        # wipe the current design (by command or before loading a new design)
        if not self.isClean():
            reply = QMessageBox.question(self, "The design has been modified.", "Do you want to save your changes?", QMessageBox.Save | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Save)
            #print "response = " + str(reply)
            if reply == QMessageBox.Save:
                self.save()
            elif reply == QMessageBox.Cancel:
                return

        self.wipe_slate()

    def open(self, startdir=None):
        if not self.isClean():
            reply = QMessageBox.question(self, "The design has been modified.", "Do you want to save your changes?", QMessageBox.Save | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Save)
            #print "response = " + str(reply)
            if reply == QMessageBox.Save:
                self.save()
            elif reply == QMessageBox.Cancel:
                return

        if startdir == None:
            startdir = os.path.expanduser("~")
        (filename, mask) = QFileDialog.getOpenFileName(self, "Open File",
                                                       startdir,
                                                       "MAdesigner (*.mad)")
        if ( filename == "" ):
            return
        self.load(str(filename))

    def open_home(self):
        startdir = os.path.expanduser("~")
        self.open(startdir)

    def load_example(self):
        basepath = os.path.split(os.path.realpath(__file__))[0]
        example_path = os.path.join(basepath, "../examples/")
        (filename, mask) = QFileDialog.getOpenFileName(None, "Open File",
                                                       example_path,
                                                       "MAdesigner (*.mad)")
        if ( filename == "" ):
            return
        self.load(filename)

    def setFileName(self):
        startdir = os.path.expanduser("~/newdesign.mad")
        (filename, mask) = QFileDialog.getSaveFileName(self, "Save File",
                                                       startdir,
                                                       "MAdesigner (*.mad)")
        return filename

    def gen_property_tree(self):
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
                
        return design
    
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

        # create the design as a property tree
        design = self.gen_property_tree()

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
            reply = QMessageBox.question(self, "The design has been modified.", "Do you want to save your changes?", QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
            #print "response = " + str(reply)
            if reply == QMessageBox.Save:
                self.save()
            elif reply == QMessageBox.Cancel:
                return

        QtCore.QCoreApplication.instance().quit()
