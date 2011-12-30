#!/usr/bin/env python
#
# Copyright (c) 2010 Matteo Boscolo
#
# This file is part of PythonCAD.
#
# PythonCAD is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# PythonCAD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PythonCAD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# This  module provide all the global variable to be used from the pythoncad Application
#
#
# This Class define a QTreeWidget implementation for showing the layer structure
#
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from PyQt4                              import QtCore, QtGui

from Kernel.initsetting                 import MAIN_LAYER
from Kernel.layer                       import Layer
from Kernel.exception                   import PythonCadWarning

NAME, VISIBLE = range(2)

class LayerItem(object):
    def __init__(self, kernelItem, id=None, active=True):
        self._kernelItem = kernelItem
        self._id = id
        self._active = active
        
    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        return self._kernelItem.name

class LayerModel(QtCore.QAbstractTableModel):
    """
    The model of the Qt Model/View pattern
    
    Represents the data in a table as a two dimensional array
    """
    def __init__(self, parent):
        super(LayerModel, self).__init__(parent)
        self.layers = []

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.layers)

    def columnCount(self, parent):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None
        layer = self.layers[index.row()]
        column = index.column()
        if role == QtCore.Qt.DisplayRole:
            if column == NAME:
                return layer._kernelItem.name
            elif column == VISIBLE:
                return layer._kernelItem.visible

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.TextAlignmentRole:
            if orientation == QtCore.Qt.Horizontal:
                return QtCore.Qt.AlignLeft
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            if section == NAME:
                return "Layer Name"
            elif section == VISIBLE:
                return "Visible"
        return None

    def removeRows(self, row, count, parent = QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        self.layers = self.layers[:row] + self.layers[row + count:]
        self.endRemoveRows()
        return True

    def clear(self):
        self.removeRows(0, self.rowCount())
        self.reset()

class LayerDelegate(QtGui.QStyledItemDelegate):

    def __init__(self, document, parent=None):
        super(LayerDelegate, self).__init__(parent)
        self._document = document

    def paint(self, painter, option, index):
        if index.column() == NAME:
            layer = index.model().layers[index.row()]
            active_layer_id = self._document.getTreeTable.getActiveLayer().getId()
            if layer.id == active_layer_id:
                painter.fillRect(option.rect, QtCore.Qt.lightGray)
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)

class LayerView(QtGui.QTableView):
    """
    The view of the Qt Model/View pattern
    
    Displays the layers in a simple table instead of a tree. This allows for
    easier management of layers.
    """
    def __init__(self, parent, document, model):
        super(LayerView, self).__init__(parent)
        self._document = document
        self.model = model
        self.setModel(self.model)
        self.setItemDelegate(LayerDelegate(self._document, self))
        # Configuration Options
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.horizontalHeader().setClickable(False)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.populateStructure()
        
        # Bug in Qt that doesn't resize rows to content on initialization
        # http://www.qtforum.org/article/13421/qtableview-how-to-make-rows-size-smaller.html
        # TODO: Find actual fix
        for row in range(self.model.rowCount()):
            self.resizeRowToContents(row)
        
        # Events
        self._document.getTreeTable.insertEvent = self.updateView
        self._document.getTreeTable.updateEvent = self.updateView
        self._document.getTreeTable.deleteEvent = self.updateView
        self._document.getTreeTable.setCurrentEvent = self.updateView

    def updateView(self, layer):
        self.model.clear()
        self.populateStructure()
        self.reset()

    def populateStructure(self):
        layers = self._document.getTreeTable.getLayers()
        activeLayer = self._document.getTreeTable.getActiveLayer()
        activeLayerId = activeLayer.getId()
        for key in layers:
            c = layers[key]
            if key == activeLayerId:
                self.model.layers.append(LayerItem(c, id=key, active=True))
            else:
                self.model.layers.append(LayerItem(c, id=key, active=False))
        self.resizeRowsToContents()

    def contextMenuEvent(self, event):
        contextMenu = QtGui.QMenu(self)
        
        addLayerAction = QtGui.QAction('New Layer', self, triggered=self._addLayer)
        renameLayerAction = QtGui.QAction('Rename Layer', self, triggered=self._rename)
        removeAction = QtGui.QAction('Remove Layer', self, triggered=self._remove)
        hideAction = QtGui.QAction('Hide', self, triggered=self._hide)
        showAction = QtGui.QAction('Show', self, triggered=self._show)
        setCurrentAction = QtGui.QAction('Set Current', self, triggered=self._setCurrent)
        
        contextMenu.addAction(addLayerAction)
        contextMenu.addAction(renameLayerAction)
        contextMenu.addAction(removeAction)
        contextMenu.addAction(hideAction)
        contextMenu.addAction(showAction)
        contextMenu.addAction(setCurrentAction)
        
        contextMenu.exec_(event.globalPos())
        del(contextMenu)

    def _addLayer(self):
        text, ok = QtGui.QInputDialog.getText(self, 'New Layer', 'Enter Layer Name')
        if ok:
            layerName = text
            newLayer = self._document.saveEntity(Layer(layerName))
            self._document.getTreeTable.insert(newLayer)

    def _remove(self):
        if self.current_selection.name == MAIN_LAYER:
            QtGui.QMessageBox.warning(self, 'Error', 'The main layer cannot be deleted')
            return False
        layerId = self.current_selection.id
        self._document.getTreeTable.delete(layerId)

    def _rename(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Rename Layer', 'Enter New Layer Name')
        if ok:
            layerId = self.current_selection.id
            self._document.getTreeTable.rename(layerId, text)

    def _hide(self):
        layerId = self.current_selection.id
        self._document.getTreeTable.hide(layerId)

    def _show(self):
        layerId = self.current_selection.id
        self._document.getTreeTable.hide(layerId, False)

    def _setCurrent(self):
        cito = self.current_selection
        if cito != None:
            self._document.getTreeTable.setActiveLayer(cito.id)

    @property
    def current_selection(self):
        layer_indexes = self.selectionModel().selectedRows()
        for index in layer_indexes:
            layer = self.model.layers[index.row()]
            if layer.id != None:
                return layer
