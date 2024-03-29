#
# Copyright (c) 2002, 2003, 2004 Art Haas
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
# miscellaneous utility functions
#

from math import fmod, pi
import types

from PythonCAD.Generic import tolerance

def get_float(val):
    _v = val
    if not isinstance(_v, float):
        if not isinstance(_v, (int, long)):
            raise TypeError, "Invalid non-numeric type: " + `type(_v)`
        _v = float(val)
    return _v

def test_boolean(val):
    if hasattr(types, 'BooleanType'):
        if not isinstance(val, types.BooleanType):
            raise TypeError, "Invalid non-boolean type: " + `type(val)`
    else:
        if val is not True and val is not False:
            raise TypeError, "Invalid non-boolean type: " + `type(val)`

def tuple_to_two_floats(t):
    if not isinstance(t, tuple):
        raise TypeError, "Argument must be a tuple: " + `type(t)`
    if len(t) != 2:
        raise ValueError, "Tuple must hold exactly two objects: " + str(t)
    _obj1, _obj2 = t
    _x = get_float(_obj1)
    _y = get_float(_obj2)
    return _x, _y

def tuple_to_three_floats(t):
    if not isinstance(t, tuple):
        raise TypeError, "Argument must be a tuple: " + `type(t)`
    if len(t) != 3:
        raise ValueError, "Tuple must hold exactly three objects: " + str(t)
    _obj1, _obj2, _obj3 = t
    _x = get_float(_obj1)
    _y = get_float(_obj2)
    _z = get_float(_obj3)
    return _x, _y, _z

def make_angle(angle):
    """Return an angle value such that -90 <= angle <= 90.

make_angle(angle)

The argument angle should be a float. Additionally the argument
is expected to be in degrees, not radians.
    """
    _angle = get_float(angle)
    if _angle < -90.0 or _angle > 90.0:
        _fa = fmod(_angle, 360.0)
        if abs(_fa) < 1e-10:
            _angle = 0.0
        elif _fa > 0.0:
            if _fa > 270.0:
                _angle = _fa - 360.0
            elif _fa > 90.0:
                _angle = _fa - 180.0
            else:
                _angle = _fa
        else:
            if _fa < -270.0:
                _angle = _fa + 360.0
            elif _fa < -90.0:
                _angle = _fa + 180.0
            else:
                _angle = _fa
    return _angle

def make_c_angle(angle):
    """Return an angle value such that 0 <= angle <= 360.

make_c_angle(angle)

The argument angle should be a float.
    """
    _a = get_float(angle)
    if _a < 0.0:
        _a = fmod(_a, 360.0) + 360.0
    elif _a > 360.0:
        _a = fmod(_a, 360.0)
    return _a

def make_coords(x, y):
    """Check and convert x/y values to float values.

make_coords(x, y)

This routine is used to ensure the values are float values.
    """
    _x = get_float(x)
    _y = get_float(y)
    return _x, _y

def make_region(xmin, ymin, xmax, ymax):
    """Return a validated region defined by (xmin, ymin) to (xmax, ymax).

make_region(xmin, ymin, xmax, ymax)

This routine is used to ensure the values are floats and
that xmin < xmax and ymin < ymax.
    """
    _xmin = get_float(xmin)
    _ymin = get_float(ymin)
    _xmax = get_float(xmax)
    if _xmax < _xmin:
        raise ValueError, "Invalid values: xmax < xmin"
    _ymax = get_float(ymax)
    if _ymax < _ymin:
        raise ValueError, "Invalid values: ymax < ymin"
    return _xmin, _ymin, _xmax, _ymax
    
def degrees(value):
    """Convert a value from radians to degrees.

degrees(value)

In Python 2.3 this is available as the math.degrees() function, but
the value isn't scaled from -360.0 <= angle <= 360.0
    """
    _value = get_float(value)
    return fmod(_value, 360.0)

def radians(value):
    """Convert a value from degrees to radians.

radians(value)

In Python 2.3 this is available ad the math.radians() function, but
the value isn't scaled from -2*pi <= angle <= 2*pi
    """
    _value = get_float(value)
    return fmod(_value, (2.0 * pi))

#
# map x/y coordinates to a (x1, y1)->(x2, y2) segment
#

def map_coords(x, y, x1, y1, x2, y2, tol=tolerance.TOL):
    """
map_coords(x, y, x1, y1, x2, y2[, tol])
    """
    _x = get_float(x)
    _y = get_float(y)
    _x1 = get_float(x1)
    _y1 = get_float(y1)
    _x2 = get_float(x2)
    _y2 = get_float(y2)
    _t = tolerance.toltest(tol)
    if ((_x < min(_x1, _x2) - _t) or
        (_y < min(_y1, _y2) - _t) or
        (_x > max(_x1, _x2) + _t) or
        (_y > max(_y1, _y2) + _t)):
        return None
    _sqlen = pow((_x2 - _x1), 2) + pow((_y2 - _y1), 2)
    if _sqlen < 1e-10: # coincident points
        return None
    _r = ((_x - _x1)*(_x2 - _x1) + (_y - _y1)*(_y2 - _y1))/_sqlen
    if _r < 0.0:
        _r = 0.0
    if _r > 1.0:
        _r = 1.0
    _px = _x1 + _r * (_x2 - _x1)
    _py = _y1 + _r * (_y2 - _y1)
    if abs(_px - _x) < _t and abs(_py - _y) < _t:
        return _px, _py
    return None

#
# test if line segments are visible within a rectangular region
#

def in_region(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    """Test if a segment from (x1, y1)->(x2, y2) is in region.

in_region(x1, y1, x2, y2, xmin, ymin, xmax, ymax)
    """
    _x1 = get_float(x1)
    _y1 = get_float(y1)
    _x2 = get_float(x2)
    _y2 = get_float(y2)
    _xmin = get_float(xmin)
    _ymin = get_float(ymin)
    _xmax = get_float(xmax)
    if _xmax < _xmin:
        raise ValueError, "Illegal values: xmax < xmin"
    _ymax = get_float(ymax)
    if _ymax < _ymin:
        raise ValueError, "Illegal values: ymax < ymin"
    if not ((_x1 < _xmin) or
            (_x1 > _xmax) or
            (_y1 < _ymin) or
            (_y1 > _ymax)):
        return True
    if not ((_x2 < _xmin) or
            (_x2 > _xmax) or
            (_y2 < _ymin) or
            (_y2 > _ymax)):
        return True
    #
    # simple horizontal/vertical testing
    #
    if abs(_y2 - _y1) < 1e-10: # horizontal
        if not ((_y1 < _ymin) or (_y1 > _ymax)):
            if min(_x1, _x2) < _xmin and max(_x1, _x2) > _xmax:
                return True
    if abs(_x2 - _x1) < 1e-10: # vertical
        if not ((_x1 < _xmin) or (_x1 > _xmax)):
            if min(_y1, _y2) < _ymin and max(_y1, _y2) > _ymax:
                return True
    #
    # see if segment intersects an imaginary segment
    # from (xmin, ymax) to (xmax, ymin)
    #
    # p1 = (xmin, ymax)
    # p2 = (xmax, ymin)
    # p3 = (x1, y1)
    # p4 = (x2, y2)
    #
    _d = ((_xmax - _xmin)*(_y2 - _y1)) - ((_ymin - _ymax)*(_x2 - _x1))
    if abs(_d) > 1e-10:
        _n = ((_ymax - _y1)*(_x2 - _x1)) - ((_xmin - _x1)*(_y2 - _y1))
        _r = _n/_d
        if 0.0 < _r < 1.0:
            return True
    #
    # see if segment intersects an imaginary segment
    # from (xmin, ymin) to (xmax, ymax)
    #
    # p1 = (xmin, ymin)
    # p2 = (xmax, ymax)
    # p3 = (x1, y1)
    # p4 = (x2, y2)
    #
    _d = ((_xmax - _xmin)*(_y2 - _y1)) - ((_ymax - _ymin)*(_x2 - _x1))
    if abs(_d) > 1e-10:
        _n = ((_ymin - _y1)*(_x2 - _x1)) - ((_xmin - _x1)*(_y2 - _y1))
        _r = _n/_d
        if 0.0 < _r < 1.0:
            return True
    return False

def to_unicode(obj, encoding='utf-8'):
    """
        Transform a string in a different format Default utf-8
    """
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj =obj.replace('\x00', '').decode(encoding, 'ignore').encode(encoding)
        return obj
    raise TypeError, "Invalid object type : " + `type(obj)`
