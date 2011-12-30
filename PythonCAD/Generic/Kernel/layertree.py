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
# This  module all the interface to store the layer
#
#TODO : REPAIR THE LOGGER FOR THIS CLASS

from Kernel.layer               import Layer
from Kernel.exception           import *
from Kernel.initsetting         import MAIN_LAYER
from Kernel.pycadevent          import PyCadEvent

class LayerTable(object):
    """
    Class used to interface with the database/save file
    """
    def __init__(self,kernel):
        self.__kr=kernel
        try:
            # TODO: Make it so the "MAIN_LAYER" isn't needed
            self.__mainLayer=self.getEntLayerDb(MAIN_LAYER)
        except EntityMissing:
            mainLayer=Layer(MAIN_LAYER)
            self.__mainLayer=self.__kr.saveEntity(mainLayer)
        except:
            raise StructuralError, "Unable to inizialize LayerTree"
        self.__activeLayer=self.__mainLayer
        self.setCurrentEvent=PyCadEvent()
        self.deleteEvent=PyCadEvent()
        self.insertEvent=PyCadEvent()
        self.updateEvent=PyCadEvent()
        
    def setActiveLayer(self, layerId):
        """
            set the active layer
        """
        activeLayer=self.__kr.getEntity(layerId)
        if activeLayer:
            self.__activeLayer=activeLayer
            self.setCurrentEvent(activeLayer)
        else:
            raise EntityMissing, "Unable to find the layer %s"%str(layerName)

    def getActiveLayer(self):
        """
            get the active layer
        """
        return self.__activeLayer

    def insert(self, layer):
        """
            Insert a new object in the class and set it as active
        """
        childEndDb = self.__kr.getEntity(layer.getId())
        if not childEndDb:
            childEndDb = self.__kr.saveEntity(layer)
        self.__activeLayer=childEndDb
        self.insertEvent(childEndDb) #Fire Event
        
    def _getLayerConstructionElement(self, pyCadEnt):
        """
            Retrive the ConstructionElement in the pyCadEnt
        """
        unpickleLayers=pyCadEnt.getConstructionElements()
        for key in unpickleLayers:
            return unpickleLayers[key]
        return None

    def getLayerChildrenLayer(self,layer):
        """
            get the layer children
            ### Unneeded ###
        """
        return self.__kr.getAllChildrenType(layer, 'LAYER')

    #************************************************************************
    #*************************layer managment********************************
    #************************************************************************
    def getLayerChildIds(self,layer):
        """
            get all the child id of a layer
            ### Unneeded ###
        """
        #manage in a better way the logger  self.__kr.__logger.debug('getLayerChild')
        _layerId=self.__kr.getEntLayerDb(layerName).getId()
        _childIds=self.__kr.__pyCadRelDb.getChildrenIds(_layerId)
        return _childIds

    def getLayerChildren(self,layer,entityType=None):
        """
            get all dbEnt from layer of type entityType
            ### Unneeded ###
        """
        _children=self.__kr.getAllChildrenType(layer,entityType)
        return _children

    def getEntLayerDb(self,layerName):
        """
            get the pycadent  layer by giving a name
        """
        #TODO: manage logger self.__logger.debug('getEntLayerDb')
        _layersEnts=self.__kr.getEntityFromType('LAYER')
        #TODO: Optimaze this loop with the build in type [...] if possible
        for layersEnt in _layersEnts:
            unpickleLayers=layersEnt.getConstructionElements()
            for key in unpickleLayers:
                if unpickleLayers[key].name==layerName:
                    return layersEnt
        else:
            raise EntityMissing,"Layer name %s missing"%str(layerName)

    def getLayers(self):
        """
        Returns a dictionary of all the layers
        """
        layers = self.__kr.getEntityFromType('LAYER')
        layer_dict = {}
        for layer in layers:
            c = self._getLayerConstructionElement(layer)
            layer_dict[layer.getId()] = c
        return layer_dict

    def getLayerTree(self):
        """
            create a dictionary with all the layer nested
        """
        rootDbEnt=self.getEntLayerDb(MAIN_LAYER)
        def createNode(layer):
            childs={}
            c=self._getLayerConstructionElement(layer)
            layers=self.getLayerChildrenLayer(layer)
            for l in layers:
                ca=self._getLayerConstructionElement(l)
                childs[l.getId()]=(ca, createNode(l))
            return childs
        c=self._getLayerConstructionElement(rootDbEnt)
        exitDb={}
        exitDb[rootDbEnt.getId()]=(c,createNode(rootDbEnt) )
        return exitDb
    
    def getLayerdbTree(self):
        """
            create a dictionary with all the layer nested as db entity
        """
        rootDbEnt=self.getEntLayerDb(MAIN_LAYER)
        def createNode(layer):
            childs={}
            layers=self.getLayerChildrenLayer(layer)
            for l in layers:
                childs[l.getId()]=(l, createNode(l))
            return childs
        exitDb={}
        exitDb[rootDbEnt.getId()]=(rootDbEnt,createNode(rootDbEnt) )
        return exitDb
        
    def getParentLayer(self,layer):
        """
            get the parent layer
            ToDo: to be tested
        """
        return self.__kr.getRelatioObject().getParentEnt(layer)

    def delete(self, layerId):
        """
            delete the current layer and all the entity related to it
        """
        deleteLayer=self.__kr.getEntity(layerId)
        if deleteLayer is self.__activeLayer:
            self.setActiveLayer(self.getEntLayerDb(MAIN_LAYER))
        self.__kr.deleteEntity(layerId)
        self.deleteEvent(layerId)

    def deleteLayerEntity(self, layer):
        """
            delete all layer entity
        """
        for ent in self.getLayerChildren(layer):
                self.__kr.deleteEntity(ent.getId())

    def rename(self, layerId, newName):
        """
            rename the layer
        """
        layer=self.__kr.getEntity(layerId)
        self._rename(layer, newName)
        self.updateEvent(layerId) # fire update event

    def _rename(self, layer, newName):
        """
            rename the layer internal use
        """
        layer.getConstructionElements()['LAYER'].name=newName
        print layer.getConstructionElements()['LAYER'].__dict__
        self.__kr.saveEntity(layer)
        self.updateEvent(layer)

    def _hide(self, layer, hide=True):
        """
            inner function for hiding the layer
        """
        # Hide/Show all the children entity
        self.hideLayerEntity(layer, hide)
        # Hide and update the layer object    
        layer.getConstructionElements()['LAYER'].visible=not hide
        self.__kr.saveEntity(layer)
        self.updateEvent(layer)
        
    def isMainLayer(self, layer):
        """
            check if the layer is the main layer
        """
        if layer.getConstructionElements()['LAYER'].name==MAIN_LAYER:
            return True
        return False
        
    def hide(self, layerId, hide=True):
        layer = self.__kr.getEntity(layerId)  
        if self.isMainLayer(layer):
            raise PythonCadWarning("Unable to hide/show the main Layer")   
        if layerId is self.__activeLayer.getId():
            self.setActiveLayer(self.getEntLayerDb(MAIN_LAYER).getId())
        self._hide(layer, hide)

    def hideLayerEntity(self, layer, hide=True):    
        """
            hide all the entity of the layer
        """
        if hide:
            for ent in self.getLayerChildren(layer):
                self.__kr.hideEntity(entity=ent)
        else:
            for ent in self.getLayerChildren(layer):
                self.__kr.unHideEntity(entity=ent)
