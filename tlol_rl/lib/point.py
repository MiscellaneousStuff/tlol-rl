# MIT License
# 
# Copyright (c) 2023 MiscellaneousStuff
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""A basic Point class."""

import collections
import math
import random

class Point(collections.namedtuple("Point", ["x", "y"])):
    """A basic Point class."""
    __slots__ = ()

    @classmethod
    def build(cls, obj):
        """Build a Point from an object that has properties `x` and `y`."""
        return cls(obj.x, obj.y)
    
    def dist(self, other):
        """Distance to some other point."""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx**2 + dy**2)
    
    def round(self):
        """Round `x` and `y` to integers."""
        return Point(int(round(self.x)), int(round(self.y)))
    
    def floor(self):
        """Round `x` and `y` down to integers."""
        return Point(int(math.floor(self.x)), int(math.floor(self.y)))
    
    def ceil(self):
        """Round `x` and `y` up to integers."""
        return Point(int(math.ceil(self.x)), int(math.ceil(self.y)))

    def abs(self):
        """Round `x` and `y` up to integers."""
        return Point(int(abs(self.x)), int(abs(self.y)))

    def normalized(self):
        """Scale `x` and `y` in-between (0, 1)"""
        return Point(self.x / self.len(), self.y / self.len())

    def len(self):
        """Length of the vector to this point."""
        return math.sqrt(self.x**2 + self.y**2)

    def transpose(self):
        """Flip x and y."""
        return Point(self.y, self.x)
    
    def rotate_deg(self, angle):
        return self.rotate_rad(math.radians(angle))

    def rotate_rad(self, angle):
        return Point(self.x * math.cos(angle) - self.y * math.sin(angle),
                 self.x * math.sin(angle) + self.y * math.cos(angle))

    def rotate_rand(self, angle=180):
        return self.rotate_deg(random.uniform(-angle, angle))

    def __str__(self):
      if all(isinstance(v, int) for v in self):
        return "%d,%d" % self
      else:
        return "%.6f,%.6f" % self

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __add__(self, pt_or_val):
      if isinstance(pt_or_val, Point):
          return Point(self.x + pt_or_val.x, self.y + pt_or_val.y)
      else:
          return Point(self.x + pt_or_val, self.y + pt_or_val)

    def __sub__(self, pt_or_val):
      if isinstance(pt_or_val, Point):
          return Point(self.x - pt_or_val.x, self.y - pt_or_val.y)
      else:
          return Point(self.x - pt_or_val, self.y - pt_or_val)

    def __mul__(self, pt_or_val):
      if isinstance(pt_or_val, Point):
          return Point(self.x * pt_or_val.x, self.y * pt_or_val.y)
      else:
          return Point(self.x * pt_or_val, self.y * pt_or_val)

    def __truediv__(self, pt_or_val):
      if isinstance(pt_or_val, Point):
          return Point(self.x / pt_or_val.x, self.y / pt_or_val.y)
      else:
          return Point(self.x / pt_or_val, self.y / pt_or_val)

    def __floordiv__(self, pt_or_val):
      if isinstance(pt_or_val, Point):
          return Point(int(self.x // pt_or_val.x), int(self.y // pt_or_val.y))
      else:
          return Point(int(self.x // pt_or_val), int(self.y // pt_or_val))

    __div__ = __truediv__
  
origin = Point(0, 0)