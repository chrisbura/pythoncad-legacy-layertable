#
# Copyright (c) 2009 Matteo Boscolo
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

import math
import types
import warnings

import pygtk
pygtk.require('2.0')
import gtk

from PythonCAD.Generic import util
from PythonCAD.Generic import intersections
from PythonCAD.Generic.point    import Point
from PythonCAD.Generic.segment  import Segment
from PythonCAD.Generic.circle   import Circle
from PythonCAD.Generic.ccircle  import CCircle
from PythonCAD.Generic.arc      import Arc
from PythonCAD.Generic.cline    import CLine
from PythonCAD.Generic.hcline   import HCLine
from PythonCAD.Generic.vcline   import VCLine
from PythonCAD.Generic.acline   import ACLine
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic.segjoint import Chamfer, Fillet

from PythonCAD.Generic import globals

class SnapPointStr(object):
    """
        this class provide a structure for cliched user point 
    """
    __snapKind=None
    __snapPoint=None
    __snapEnt=None
    __snapCursor=gtk.gdk.Cursor(gtk.gdk.X_CURSOR)
    
    def __init__(self,k,p,e):
        self.kind=k
        self.point=p
        self.entity=e
        
    def getKind(self):
        return self.__snapKind
    
    def setKind(self,k):
        self.__snapKind=k
        
    def getPoint(self):
        return self.__snapPoint
    
    def setPoint(self,p):
        if not isinstance(p,Point):
            raise TypeError, "Invalid Point type : " + `type(p)`
        self.__snapPoint=p
        
    def getEnt(self):
        return self.__snapEnt
    
    def setEnt(self,e):
        self.__snapEnt=e
        
    def getCursor(self):
        return self.__snapCursor
    
    def setCursor(self,c):
        self.__snapCursor=c
        
    kind=property(getKind,setKind,None,"Set/Get the kind of snap that is required")
    point=property(getPoint,setPoint,None,"Set/get the Point clicked that is required")
    entity=property(getEnt,setEnt,None,"Set/Get the Entity Clicked")
    cursor=property(getCursor,setCursor,None,"Define the Cursor")

    
class SnapServices(object):
    """
        Provide all snap functionality for the user
    """
    def __init__(self,image):
        self.__image=image
        self.__topLayer=image.getTopLayer()
        self.__temporarySnap=None
        
    def getSnap(self,t,snapArray=None):
        """
            return a snap snapPointStr clicked by the user 
        """
        if snapArray is None:
            _snapArray = globals.snapOption
        else:
            _snapArray = snapArray
        _mousePoint = self.__image.getCurrentPoint()

        #print "Debug: Mouse Point %s"%str(_mousePoint)
        _mouseEnt = self.getEnt(_mousePoint, t)
        retObj = SnapPointStr("Freepoint",_mousePoint,_mouseEnt)
        retObj.cursor = gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_ARROW)            
        if self.__temporarySnap is not None:
            _snapArray=self.__temporarySnap 
        if 'mid' in  _snapArray:
            if _snapArray['mid']:
                _midPnt=self.getMid(_mousePoint, t)
                if  _midPnt != None:
                    retObj.point=_midPnt
                    retObj.kind="Mid"
                    retObj.cursor=gtk.gdk.Cursor(gtk.gdk.SB_H_DOUBLE_ARROW)
        if 'end' in  _snapArray:
            if _snapArray['end']:
                _endPnt=self.getEndPoint(_mousePoint,_mouseEnt)
                if _endPnt != None:
                    if retObj.kind=="Freepoint":
                        retObj.point=_endPnt 
                        retObj.kind="End"
                        retObj.cursor=gtk.gdk.Cursor(gtk.gdk.DOTBOX)
                    if _mousePoint.Dist(_endPnt)<_mousePoint.Dist(retObj.point):
                        retObj.point=_endPnt
                        retObj.kind="End"
                        retObj.cursor=gtk.gdk.Cursor(gtk.gdk.DOTBOX)
        if 'intersection' in  _snapArray:
            if _snapArray['intersection']:
                _intPnt=self.getIntersection(_mousePoint,t)
                if _intPnt != None:
                    if retObj.kind=="Freepoint":
                        retObj.point=_intPnt
                        retObj.kind="Mid"
                        retObj.cursor=gtk.gdk.Cursor(gtk.gdk.X_CURSOR)
                    if _mousePoint.Dist(_intPnt)<_mousePoint.Dist(retObj.point):
                        retObj.point=_intPnt
                        retObj.kind="Mid"
                        retObj.cursor=gtk.gdk.Cursor(gtk.gdk.X_CURSOR)
        if 'point' in _snapArray:
            if _snapArray['point']:
                _pntPnt=self.getPoint(_mousePoint,t)
                if _pntPnt != None:
                    if retObj.kind=="Freepoint":
                        retObj.point=_pntPnt
                        retObj.kind="Point"
                        retObj.cursor=gtk.gdk.Cursor(gtk.gdk.IRON_CROSS)
                    if _mousePoint.Dist(_pntPnt)<_mousePoint.Dist(retObj.point):
                        retObj.point=_pntPnt
                        retObj.kind="Point"
                        retObj.cursor=gtk.gdk.Cursor(gtk.gdk.IRON_CROSS)
        if 'origin' in  _snapArray:
            if _snapArray['origin']:
                _oriPnt=Point(0.0,0.0)
                retObj.point=_oriPnt
                retObj.kind="Origin"
                retObj.cursor=gtk.gdk.Cursor(gtk.gdk.DOT)
                return retObj
        if 'perpendicular' in  _snapArray:
            if _snapArray['perpendicular']:
                retObj.point=Point(_mousePoint)
                retObj.kind="Perpendicular"
                retObj.cursor=gtk.gdk.Cursor(gtk.gdk.BOTTOM_TEE)
                return retObj
        if 'tangent' in _snapArray:
            if _snapArray['tangent']:
                retObj.point=_mousePoint
                retObj.kind="Tangent"
                retObj.cursor=gtk.gdk.Cursor(gtk.gdk.EXCHANGE)
                return retObj
        if 'center' in _snapArray:
            if _snapArray['center']:
                _cenPnt=self.getCenter(_mousePoint,t)
                if _cenPnt != None:
                    retObj.point=_cenPnt
                    retObj.kind="Center"
                    retObj.cursor=gtk.gdk.Cursor(gtk.gdk.CIRCLE)
                    return retObj
        return retObj
    
    
    def getEnt(self, point, _t, types=None):
        """
            Get The Entity Under the Mouse Pointer
        """
        _objlist = []
        _intlist = []

        x, y = point.getCoords()
        
        if types is not None:
            _types = types
        else:
            _types = {'point' : True,
                  'segment' : True,
                  'circle' : True,
                  'arc' : True,
                  'polyline' : True,
                  'hcline' : True,
                  'vcline' : True,
                  'acline' : True,
                  'cline' : True,
                  'ccircle' : True,
                  }
        _layers = [self.__image.getActiveLayer()]
        while len(_layers):
            _layer = _layers.pop()
            _hits = _layer.mapCoords(x, y, tolerance=_t, types=_types)
            if len(_hits) > 0:
                for _obj, _pt in _hits:
                    if(_obj is not None):
                        return _obj
        return None
    
    def getMid(self, point, t):
        """"
            Calculate the mid point 
        """
        _types = {'segment' : True}
        _obj = self.getEnt(point, t,_types)
        if _obj is None:
            return None
        _ix,_iy =_obj.getMiddlePoint()
        return Point(_ix,_iy)
    

    def getEndPoint(self, point, entityHits):
        """
            Get The Segment End Point nearest to the coord x,y            
        """
        if not entityHits is None:            
            if isinstance(entityHits, Segment):
                _op1, _op2 = entityHits.getEndpoints()
                if(point.Dist(_op1) < point.Dist(_op2)):
                    return _op1
                else:
                    return _op2
        return None  
    
    
    def getIntersection(self, point, t):
        """
            Calculate the intersection point
        """
        _objlist = []
        _intlist = []

        x, y = point.getCoords()
        
        _types = {'point':False,
                  'segment' : True,
                  'circle' : True,
                  'arc' : True,
                  'polyline' : True,
                  'hcline' : True,
                  'vcline' : True,
                  'acline' : True,
                  'cline' : True,
                  'ccircle' : True,
                  }
        _layers = [self.__topLayer]
        
        while len(_layers):
            _layer = _layers.pop()
            _hits = _layer.mapCoords(x, y, tolerance=t, types=_types)
            if len(_hits) > 0:
                for _obj, _pt in _hits:
                    for _tobj, _mp in _objlist:
                        for _ix, _iy in intersections.find_intersections(_tobj, _obj):
                            if ((abs(_ix - x) < t) and
                                (abs(_iy - y) < t)):
                                _sqlen = pow((x - _ix), 2) + pow((y - _iy), 2)
                                _intlist.append((_sqlen, (_ix, _iy)))
                    _objlist.append((_obj, _pt))
            _layers.extend(_layer.getSublayers())
        #
        # use the nearest intersection point if one is available
        #
        if len(_intlist):
            _intlist.sort()
            _cp = _intlist[0][1]
            if _cp is not None:
                return Point(_cp[0],_cp[1])
        return None
    
    
    def getCenter(self, point, t):
        """
            Get The Center point over the mouse
        """
        
        _types = { 'ccircle' : True
        ,'ccircle' : True
        ,'circle' : True
        ,'arc' : True
        ,'fillet':True }
        
        _obj = self.getEnt(point, t, _types)
        if _obj is None:
            return None
        return _obj.getCenter()

    
    def getPoint(self, point, t):
        """
            Get The point over the mouse
        """
        _types = {'point' : True}
        _obj = self.getEnt(point, t, _types)
        if _obj is None:
            return None
        return _obj

    
    def setOneTemporarySnap(self, snap):
        """
            Set only One snap 
            snap mast be a string 
            es: 'mid'
        """
        _array = {}
        _array[snap] = True
        self.__temporarySnap = _array
        
        
    def setTemporarySnapArray(self, snapArray):
        """
            set to temporary snap array
            snapArray Mast be a dic 
            es: {'mid':true,'end':false,....}
        """
        if not isinstance(snapArray, dict):
            raise TypeError, "Unexpected type for snapArray: " + `type(snapArray)`
        self.__temporarySnap = snapArray
        
        
    def excludeSnapArray(self, excludeSnap):
        """
            set the value of the exludeSnap to the global snap 
        """
        if not isinstance(excludeSnap,dict):
            raise TypeError, "Unexpected type for snapArray: " + `type(excludeSnap)`
        self.__temporarySnap = globals.snapOption.copy()
        for key in excludeSnap.keys():
            self.__temporarySnap[key]=excludeSnap[key]

    def resetTemporatySnap(self):
        """
            Reset the temporary snap array
            and restor the normal snap flow
        """
        self.__temporarySnap=None

        
def setSnap(image, toolFunction, tol, excludeSnap=None):
    """
        set the snap to the toolFunctionMethod
        image           : image or GTKImage
        toolFunction    : function to be called for storing the data
        tol             : tollerance culd be None if image is GTKImage
        excludeSnap     : array of type {'end':False}
    """
    _sPnt=getSnapPoint(image,tol,excludeSnap)
    toolFunction(_sPnt )
    
def setDinamicSnap(gtkimage, toolFunction, excludeSnap=None):
    """
        set the dinamic snap for using withe preview douring motion functions
    """
    _tol=gtkimage.getTolerance()
    _image=gtkimage.getImage()   
    _sp=_image.snapProvider
    if excludeSnap is not None:
        _sp.excludeSnapArray(excludeSnap)
    _sPnt=_sp.getSnap(_tol)
    toolFunction(_sPnt )
    
def getSnapPoint(image,tol,excludeSnap=None):
    """
        return the snap point clicked by the user
        image           : image 
        tol             : tollerance culd be None if image is GTKImage
        excludeSnap     : array of type {'end':False,.....}
        return: SnapPointStr
    """
    _sp=image.snapProvider
    if excludeSnap is not None:
        _sp.excludeSnapArray(excludeSnap)
    _sPnt=_sp.getSnap(tol)
    _sp.resetTemporatySnap()
    return _sPnt 

def getOnlySnap(image,tol,onlySnapArray):
    """
        set the dinamic snap to get only the onlySnapArray
    """
    _sPnt=None
    _sp=image.snapProvider
    if onlySnapArray is not None:
        _sp.setTemporarySnapArray(onlySnapArray)
        _sPnt=_sp.getSnap(tol)
    _sp.resetTemporatySnap()
    return _sPnt 

def getSnapOnTruePoint(gtkimage,excludeArray):
    """
        looking for real Entity Point Snap ..
        if it dose not find Return None On the str.Point
    """
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _sp=_image.snapProvider
    _strPnt=getSnapPoint(_image,_tol,excludeArray)
    _pt=getDrawedPoint(_image,_tol,_strPnt)
    if _pt is not None :
        _strPnt.point=_pt
    else:
        _active_layer = _image.getActiveLayer()
        _active_layer.addObject(_strPnt.point)
    return _strPnt

def getDrawedPoint(image ,tol,strPoint):
    """
        Looking in the drawing if the point exsists
        and get it none if no point is found
    """
    if strPoint.kind=="Freepoint": return None
    _x, _y = strPoint.point.getCoords()
    _layers = [image.getTopLayer()]
    while len(_layers):
        _layer = _layers.pop()
        if _layer.isVisible():
            _pt = None
            _pts = _layer.find('point', _x, _y, tol)
            if len(_pts) > 0:
                _pt = _pts[0]
            if _pt is not None:
                return _pt
        _layers.extend(_layer.getSublayers())
    return None 

def getSelections(gtkimage,objFilter=None):
    """
        get the first object  selected
        objFilter arguments:
        All: filter on all the entity
        None : filter on segment
        Segment Arc ... filter on the entity 
        Multiple object selection could be declared as:
        Segment,Arc,CCircle
    """
    _retVal=[]
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    if _image.hasSelection():
        _image.clearSelectedObjects()
    _x, _y = _image.getCurrentPoint()
    _active_layer = _image.getActiveLayer()
    _objs=_active_layer.mapPoint((_x, _y), _tol)
    if len(_objs):
        _mapObj ,point = _objs[0]  
        if objFilter==None: 
            if isinstance(_mapObj,Segment):
                return _mapObj,point
        elif objFilter=="All":
            return _mapObj,point
        else:
            _res=False
            exec '_res=isinstance(_mapObj,(' + str(objFilter) + '))'
            if _res:
                return _mapObj,point
    return None,None
