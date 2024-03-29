#
# Copyright (c) 2002, Art Haas
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
# define __all__ so 'from Generic import *' works
#

entitys=[
    'acline',
    'arc',
    'baseobject',
    'ccircle',
    'circle',
    'cline',
    'color',
    'conobject',
    'delete',
    'dimension',
    'dimtrees',
    'dim12',
    'dim1314',
    'dim15',
    'dwgbase',
    'dwgutil',
    'dxf',
    'ellipse',
    'entity',
    'fileio',
    'globals',
    'graphicobject',
    'hatch',
    'hcline',
    'image',
    'imageio',
    'intersections'
    'keywords'
    'layer',
    'leader',
    'linetype',
    'logger',
    'maptree',
    'message',
    'mirror',
    'move',
    'nurbs',
    'options',
    'plotfile',
    'point',
    'polyline',
    'preferences',
    'printing',
    'prompt',
    'quadtree',
    'segjoint',
    'segment',
    'selections',
    'split',
    'style',
    'tangent',
    'text',
    'tolerance',
    'tools',
    'transfer',
    'tree',
    'units'
    'util',
    'vcline'
    ]


__all__=[]
for subpackage in entitys:
    try: 
        exec 'from ' + subpackage + ' import *'
        __all__.append( subpackage )
    except ImportError:
        pass


