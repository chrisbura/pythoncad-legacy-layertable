
import math
from PyQt4 import QtCore, QtGui


class CadView(QtGui.QGraphicsView):
    
    def __init__(self, parent=None):
        super(CadView, self).__init__(parent)
        
    
    def __init__(self, scene, parent=None):
        super(CadView, self).__init__(scene, parent)
        
        
    def sizeHint(self):
        return QtCore.QSize(800,600)
    
    
    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))
    

    def scaleView(self, factor):
##        factor = self.matrix().scale(factor, factor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
##
##        if factor < 0.07 or factor > 100:
##            return

        self.scale(factor, factor)
        
        