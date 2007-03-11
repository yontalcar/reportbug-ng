# MyMainWindow.py - Mainwindow of Reportbug-NG.
# Copyright (C) 2007  Bastian Venthur
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


from MainWindow import Form
from SubmitDialog import SubmitDialog
from lib.Bugreport import Bugreport
from lib import DebianBTS
from lib.ReportbugNG import *


class MyMainWindow(Form):
    
    def __init__(self):
        Form.__init__(self)
        self.bugs = []
        self.visibleBugs = []
        self.currentPackage = ""
        self.currentBug = Bugreport(0)
      
        # For debugging purpose only:
        # self.pushButtonNewBugreport.setEnabled(1)
    
    
    def lineEdit_returnPressed(self):
        """The user changed the text in the combobox and pressed enter."""
        
        self.currentPackage = unicode(self.lineEdit.text())
        self.lineEdit.setText("")
        self.textBrowser.setText("<h2>Fetching bugreports for package %s, please wait.</h2>" % self.currentPackage)
        self.pushButtonNewBugreport.setEnabled(1)
    
        self.bugs = []
        
        self.bugs = DebianBTS.getBugsByPackage(self.currentPackage)
        self.visibleBugs = self.bugs

        self.listBox.clear()
        for bug in self.visibleBugs:
            self.listBox.insertItem(str(bug))
	    
        if len(self.visibleBugs) == 0:
            self.textBrowser.setText("<h2>No bugreports for package %s found!</h2>" % self.currentPackage)
        else:
            self.textBrowser.setText("<h2>Click on a bugreport to see the full text.</h2>")
        

    def lineEdit_textChanged(self, a0):
        """The filter text has changed."""
        
        self.visibleBugs = []
        self.listBox.clear()
        
        for bug in self.bugs:
            if str(bug).lower().find(a0.lower()) != -1:
                self.visibleBugs.append(bug)
                self.listBox.insertItem(str(bug))        

        
    def listBox_highlighted(self,a0):
        """The user selected a Bug from the list."""
        
        self.listBox.update()
        self.pushButtonAdditionalInfo.setEnabled(1)
        
        self.currentBug = self.visibleBugs[a0]
        
        # Fetch the fulltext if not yet available.
        if len(self.visibleBugs[a0].fulltext) == 0:
            self.visibleBugs[a0].fulltext = DebianBTS.getFullText(self.visibleBugs[a0].nr)
        
        self.textBrowser.setText(self.visibleBugs[a0].fulltext)
        
    
    def pushButtonAdditionalInfo_clicked(self):
        """The user wants to provide additional info for the current bug."""
    
        package = self.currentPackage
        version = getInstalledPackageVersion(package)
        
        dialog = SubmitDialog()
        dialog.lineEditPackage.setText(package)
        dialog.lineEditVersion.setText(version)
        dialog.comboBoxSeverity.setEnabled(0)
        dialog.checkBoxSecurity.setEnabled(0)
        dialog.checkBoxPatch.setEnabled(0)
        dialog.checkBoxL10n.setEnabled(0)
        
        if dialog.exec_loop() == dialog.Accepted:
            subject = unicode(dialog.lineEditSummary.text())
            mua = dialog.comboBoxMUA.currentText().lower()
            package = dialog.lineEditPackage.text()
            version = dialog.lineEditVersion.text()
            to = "%s@bugs.debian.org" % self.currentBug.nr
            
            prepareMail(mua, createMailtoString(to, subject, package, version))

    
    def pushButtonNewBugreport_clicked(self):
        """The User wants to file a new bugreport against the current package."""
        
        package = self.currentPackage
        version = getInstalledPackageVersion(package)
        
        dialog = SubmitDialog()
        dialog.lineEditPackage.setText(package)
        dialog.lineEditVersion.setText(version)
        
        if dialog.exec_loop() == dialog.Accepted:
            subject = unicode(dialog.lineEditSummary.text())
            severity = dialog.comboBoxSeverity.currentText().lower()
            tags = []
            if dialog.checkBoxL10n.isChecked():
                tags.append("l10n")
            if dialog.checkBoxPatch.isChecked():
                tags.append("patch")
            if dialog.checkBoxSecurity.isChecked():
                tags.append("security")
            
            mua = dialog.comboBoxMUA.currentText().lower()
            package = dialog.lineEditPackage.text()
            version = dialog.lineEditVersion.text()
            to = "submit@bugs.debian.org"
            
            prepareMail(mua, createMailtoString(to, subject, package, version, severity, tags))

    
    def textBrowser_linkClicked(self,a0):
        """The user clicked a link in the Bugreport."""
        
        callBrowser(a0)
        # Hack to open link in external Browser: just reload the current bugreport
        self.textBrowser.setText(self.currentBug.fulltext)
