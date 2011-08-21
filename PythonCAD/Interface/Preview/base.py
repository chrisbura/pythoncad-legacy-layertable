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
# You should have received a copy of the GNU General Public Licensesegmentcmd.py
# along with PythonCAD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#This module provide a class for the segment command
#
from PyQt4 import QtCore, QtGui


from Kernel.exception       import *
from Kernel.GeoEntity.point import Point as GeoPoint
from Kernel.GeoUtil.geolib  import Vector
from Kernel.initsetting     import PYTHONCAD_COLOR, PYTHONCAD_PREVIEW_COLOR

class BaseQtPreviewItem(QtGui.QGraphicsItem):
    showShape=False # This Flag is used for debug porpoise
    showBBox=False  # This Flag is used for debug porpoise

    def __init__(self, command):
        super(BaseQtPreviewItem, self).__init__()
        self.updateColor()
        self.value=[]
        for dValue in command.defaultValue:
            val=self.convertToQTObject(dValue)
            self.value.append(val)

    def updateColor(self):
        """
            update the preview color
        """
        r, g, b=PYTHONCAD_PREVIEW_COLOR
        self.color = QtGui.QColor.fromRgb(r, g, b)

    def updatePreview(self,  position, distance, kernelCommand):
        """
            update the data at the preview item
        """
        for i in range(0, len(kernelCommand.value)):
            print "update preview value %s"%str(kernelCommand.value[i])
            self.value[i]=kernelCommand.value[i]
        # Assing Command Values
        index=kernelCommand.valueIndex
        try:
            raise kernelCommand.exception[index](None)
        except(ExcPoint):
            self.value[index]=position
        except(ExcLenght, ExcInt):
            self.value[index]=distance
        except(ExcAngle):
            p1=GeoPoint(0.0, 0.0)
            p2=GeoPoint(position.x(), position.y()*-1.0)
            self.value[index]=Vector(p1, p2).absAng
        except:
            print "updatePreview: Exception not managed"
            return
        print "Updated Index %s with value %s"%(str(index), str(self.value[index]))
        self.update(self.boundingRect())

    def paint(self, painter,option,widget):
        """
            overloading of the paint method
        """
        #draw geometry
        if self.showShape:
            r, g, b= PYTHONCAD_COLOR["cyan"]
            painter.setPen(QtGui.QPen(QtGui.QColor.fromRgb(r, g, b)))
            painter.drawPath(self.shape())

        if self.showBBox:
            r, g, b= PYTHONCAD_COLOR["darkblue"]
            painter.setPen(QtGui.QPen(QtGui.QColor.fromRgb(r, g, b)))
            painter.drawRect(self.boundingRect())

        self.drawGeometry(painter,option,widget)
        return

    def convertToQTObject(self, value):
        """
            convert the imput value in a proper value
        """
        if isinstance(value, (float, int)):
            return value
        elif isinstance(value, tuple):
            return QtCore.QPointF(value[0], value[1])
        elif isinstance(value, GeoPoint):
            return QtCore.QPointF(value.x, value.y*-1.0)
        else:
            return value

    def shape(self):
        """
            overloading of the shape method
        """
        painterStrock=QtGui.QPainterPathStroker()
        path=QtGui.QPainterPath()
        self.drawShape(path)
        painterStrock.setWidth(10)
        path1=painterStrock.createStroke(path)
        return path1

    def drawShape(self, path):
        pass

    def boundingRect(self):
        """
            overloading of the qt bounding rectangle
        """
        return self.shape().boundingRect()

