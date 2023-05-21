import typing
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QModelIndex, QObject
from pyjsa.profiles import Profile, PyJSATable
from itertools import islice

class DatabaseListModel(QtCore.QAbstractListModel):
    def __init__(self, table: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.table = PyJSATable(table)
        
                        
    def data(self, index: QModelIndex, role: int = ...):
        if role == Qt.DisplayRole:
            names = self.table.get_column("name")
            return names[index.row()]
    
    def rowCount(self, parent: QModelIndex = ...) -> int:
        return self.table.count
        