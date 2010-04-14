

from PyQt4 import QtCore, QtGui

class Segment(QtGui.QGraphicsLineItem):
    
    def __init__(self, entity):
        super(Segment, self).__init__()
        pt_begin = None
        pt_end = None
        # get the geometry
        geometry = entity.getConstructionElements()
        # get the begin and endpoint from the geometry
        for key in geometry.keys():
            if pt_begin == None:
                pt_begin = geometry[key]
            else:
                pt_end = geometry[key]
        # set the line
        self.setLine(pt_begin.x, -1.0 * pt_begin.y, pt_end.x, -1.0 * pt_end.y)
        # set pen accoording to layer
        self.setPen(QtGui.QPen(QtGui.QColor.fromRgb(255, 0, 0)))
        return
    
