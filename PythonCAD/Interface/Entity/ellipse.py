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
# qt ellipse class
#
from Interface.Entity.base import *

class Ellipse(BaseEntity):
    
    def __init__(self, entity):
        super(Ellipse, self).__init__(entity)
        geoEnt=self.geoItem
        self.xc,self.yc=geoEnt.center.getCoords()
        self.yc=self.yc*-1.0
        self.h=geoEnt.verticalRadius
        self.w=geoEnt.horizontalRadius
        return

    def drawShape(self, painterPath):    
        """
            overloading of the shape method 
        """
        painterPath.addEllipse(self.xc-(self.w/2.0),self.yc-(self.h/2.0),self.w,self.h )     
    
    def drawGeometry(self, painter, option, widget):
        """
            overloading of the paint method
        """
        #   Create Ellipse
        painter.drawEllipse(self.xc-(self.w/2.0),self.yc-(self.h/2.0),self.w,self.h)

