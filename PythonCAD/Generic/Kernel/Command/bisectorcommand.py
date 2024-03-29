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
#This module provide a class for the bisector command
#
from Kernel.exception                      import *
from Kernel.composedentity                 import ComposedEntity
from Kernel.Command.basecommand            import *
from Kernel.GeoComposedEntity.bisector     import Bisector
from Kernel.GeoEntity.segment              import Segment
from Kernel.GeoUtil.util                    import getIdPoint

class BisectorCommand(BaseCommand):
    """
        this class rappresent the champfer command
    """
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        self.exception=[ExcEntityPoint,
                        ExcEntityPoint, 
                        ExcLenght]
        self.defaultValue=[None, None, 100]
        self.message=[  "Select the First Segment: ", 
                        "Select the Second Segment: ", 
                        "Give me the Bisector Lengh: "]
        
    def getEntsToSave(self):
        """
            get the chamfer segments
        """
        id0, p0=self.value[0]
        id1, p1=self.value[1]
        objEnt=[]
        ent1=self.document.getEntity(id0)
        ent2=self.document.getEntity(id1)
        
        cel1=ent1.getConstructionElements()
        seg1=Segment(cel1)
        
        cel2=ent2.getConstructionElements()
        seg2=Segment(cel2)
        arg={
             "OBJECTJOINT_0":seg1,
             "OBJECTJOINT_1":seg2,  
             "OBJECTJOINT_2":p0, 
             "OBJECTJOINT_3":p1, 
             "OBJECTJOINT_5":self.value[2], 
             }

        cmf=Bisector(arg)
        bisectorSegment = cmf.getReletedComponent()
        objEnt.append(bisectorSegment)
        return objEnt
        
    def applyCommand(self):
        """
            apply the champfer command
        """
        if len(self.value)!=3:
            raise PyCadWrongInputData("Wrong number of input parameters")
        for _ent in self.getEntsToSave():
            self.document.saveEntity(_ent)
       
