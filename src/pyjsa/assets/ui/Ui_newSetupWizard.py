# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Workspace\pyjsa\src\pyjsa\assets\ui\newSetupWizard.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_NewSetupWizard(object):
    def setupUi(self, NewSetupWizard):
        NewSetupWizard.setObjectName("NewSetupWizard")
        NewSetupWizard.resize(677, 581)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(NewSetupWizard.sizePolicy().hasHeightForWidth())
        NewSetupWizard.setSizePolicy(sizePolicy)
        NewSetupWizard.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        NewSetupWizard.setSizeGripEnabled(False)
        NewSetupWizard.setWizardStyle(QtWidgets.QWizard.ClassicStyle)
        self.pageName = QtWidgets.QWizardPage()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pageName.sizePolicy().hasHeightForWidth())
        self.pageName.setSizePolicy(sizePolicy)
        self.pageName.setTitle("")
        self.pageName.setObjectName("pageName")
        self.formLayout = QtWidgets.QFormLayout(self.pageName)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.pageName)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.lineEditExperimentName = QtWidgets.QLineEdit(self.pageName)
        self.lineEditExperimentName.setObjectName("lineEditExperimentName")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEditExperimentName)
        NewSetupWizard.addPage(self.pageName)
        self.pageProcess = QtWidgets.QWizardPage()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pageProcess.sizePolicy().hasHeightForWidth())
        self.pageProcess.setSizePolicy(sizePolicy)
        self.pageProcess.setSubTitle("")
        self.pageProcess.setObjectName("pageProcess")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.pageProcess)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.processForm = ProcessFormWidget(self.pageProcess)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.processForm.sizePolicy().hasHeightForWidth())
        self.processForm.setSizePolicy(sizePolicy)
        self.processForm.setObjectName("processForm")
        self.horizontalLayout.addWidget(self.processForm)
        NewSetupWizard.addPage(self.pageProcess)
        self.wizardPage2 = QtWidgets.QWizardPage()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.wizardPage2.sizePolicy().hasHeightForWidth())
        self.wizardPage2.setSizePolicy(sizePolicy)
        self.wizardPage2.setObjectName("wizardPage2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.wizardPage2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.dispersionForm = DispersionFormWidget(self.wizardPage2)
        self.dispersionForm.setObjectName("dispersionForm")
        self.horizontalLayout_2.addWidget(self.dispersionForm)
        NewSetupWizard.addPage(self.wizardPage2)
        self.wizardPage = QtWidgets.QWizardPage()
        self.wizardPage.setObjectName("wizardPage")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.wizardPage)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.polingForm = PolingFormWidget(self.wizardPage)
        self.polingForm.setObjectName("polingForm")
        self.horizontalLayout_3.addWidget(self.polingForm)
        NewSetupWizard.addPage(self.wizardPage)

        self.retranslateUi(NewSetupWizard)
        QtCore.QMetaObject.connectSlotsByName(NewSetupWizard)

    def retranslateUi(self, NewSetupWizard):
        _translate = QtCore.QCoreApplication.translate
        NewSetupWizard.setWindowTitle(_translate("NewSetupWizard", "New Setup"))
        self.label.setText(_translate("NewSetupWizard", "Setup name"))
        self.lineEditExperimentName.setPlaceholderText(_translate("NewSetupWizard", "Name"))
from pyjsa.widgets import DispersionFormWidget, PolingFormWidget, ProcessFormWidget