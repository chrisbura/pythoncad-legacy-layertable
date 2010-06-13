#
# Copyright (c) ,2010 Matteo Boscolo
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
# qt text class
#

from Interface.Entity.baseentity import *

class Text(BaseEntity):
    def __init__(self, entity):
        super(Text, self).__init__(entity)
        geoEnt=self.geoItem
        self.text=geoEnt.text#QtCore.QString(geoEnt.text)
        x, y=geoEnt.location.getCoords()
        self.location=QtCore.QPointF(float(x), -1.0*y) 
        self.font=QtGui.QFont() #This have to be derived from the geoent as son is implemented
        return
        
    def boundingRect(self):
        """
            overloading of the qt bounding rectangle
        """
        return QtCore.QRectF(self.location.x(),self.location.y()  ,10.0,10.0)

    def drawShape(self, painterPath):    
        """
            overloading of the shape method 
        """
        painterPath.addText(self.location, self.font, self.text)
        
    def drawGeometry(self, painter, option, widget):
        #Create Segment
        painter.drawText(self.location, self.text)
        
        
