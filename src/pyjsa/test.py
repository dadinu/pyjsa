import sys
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QDoubleValidator
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QStyledItemDelegate
from pyjsa.gui import start_gui

class AgeDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if index.column() == 1:
            editor.setValidator(QDoubleValidator())
        return editor

class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 300, 300)
        self.setWindowTitle('Tree View Example')

        # create a dictionary with some data
        data = {'Name': 'John', 'Age': 30, 'Gender': 'Male'}
        self.treeView = QTreeView(self)
        # create a standard item model and add items to it
        model = QStandardItemModel()
        parentItem = model.invisibleRootItem()
        for key, value in data.items():
            keyItem = QStandardItem(key)
            valueItem = QStandardItem(str(value))
            if key == 'Age':
                valueItem.setFlags(valueItem.flags() | Qt.ItemIsEditable)
                delegate = AgeDelegate(self)
                self.treeView.setItemDelegateForColumn(1, delegate)
            parentItem.appendRow([keyItem, valueItem])

        # create a tree view and set its model
        self.treeView.setModel(model)
        self.treeView.setHeaderHidden(True)
        self.treeView.expandAll()
        self.treeView.setUniformRowHeights(True)

        self.show()

if __name__ == '__main__':
    """app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())"""
    start_gui()
