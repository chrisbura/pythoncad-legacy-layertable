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
from Kernel.exception               import *
from Kernel.Command.basecommand     import *
from Kernel.GeoEntity.text             import Text

class TextCommand(BaseCommand):
    """
        This class represent the segment command
    """
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        self.exception=[ExcPoint, ExcText, ExcAngle,ExcText ]
        self.defaultValue=[None, "Dummy Text", 0, "sw"]
        self.message=["Give Me the Insert Point: ",
                        "Type The Text String: ",
                        "Give Me The Rotation Angle [0]: ", 
                        "Give me a Point to Justify Text [sw]: "]

    def applyCommand(self):
        if len(self.value)!=4:
            raise PyCadWrongInputData("Wrong number of input parameter")
        textArgs={"TEXT_0":self.value[0], "TEXT_1":self.value[1], "TEXT_2":self.value[2], "TEXT_3":self.value[3]}
        text=Text(textArgs)
        self.document.saveEntity(text)
