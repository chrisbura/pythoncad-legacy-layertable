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
#This module provide a class for the fillet command
#
from Kernel.exception                      import *
from Kernel.composedentity                 import ComposedEntity
from Kernel.Command.basecommand            import *
from Kernel.GeoComposedEntity.fillet       import Fillet
from Kernel.GeoEntity.segment              import Segment
from Kernel.GeoUtil.util                    import getIdPoint

class FilletCommand(BaseCommand):
    """
        this class rappresent the champfer command
    """
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        self.exception=[ExcEntityPoint,
                        ExcEntityPoint, 
                        ExcText, 
                        ExcLenght]
        self.defaultValue=[None, None,"BOTH",10]
        self.message=[  "Give me the first  Entity ID,end a point Es(4@10,20)", 
                        "Give me the second Entity ID,end a point Es(4@10,20)", 
                        "Give me trim Mode (FIRST,SECOND,BOTH,NO_TRIM)", 
                        "Give me the radius" 
                        ]
    def getEntsToSave(self):
        """
            get the fillet segments
        """
        id0, p0=getIdPoint(self.value[0])
        id1, p1=getIdPoint(self.value[1])
        
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
             "OBJECTJOINT_2": p0, 
             "OBJECTJOINT_3": p1, 
             "OBJECTJOINT_4":self.value[2], 
             "OBJECTJOINT_5":self.value[3]
             }

        fillet=Fillet(arg)
        seg1Mod, seg2Mod, filletArc = fillet.getReletedComponent()
        
        _cElements1, entityType=self.document._getCelements(seg1Mod)
        _cElements2, entityType=self.document._getCelements(seg2Mod)
       
        ent1.setConstructionElements(_cElements1)
        ent2.setConstructionElements(_cElements2)
        
        objEnt.append(ent1)
        objEnt.append(ent2)
        
        objEnt.append(filletArc)
        return objEnt
        
    def applyCommand(self):
        """
            apply the champfer command
        """
        if len(self.value)!=4:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        try:
            self.document.startMassiveCreation()
            for _ent in self.getEntsToSave():
                self.document.saveEntity(_ent)
        finally:
            self.document.stopMassiveCreation()
       
