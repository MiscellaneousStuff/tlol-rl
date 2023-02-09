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
"""The library and base Map for map definitions.

To use a map, either import the map module and instantiate the map directly, or
import the maps lib and use `ghet`. Using `get` from this lib will work, but only
if you've imported the map module somewhere.
"""

import os

from absl import logging


class DuplicateMapError(Exception):
    pass


class NoMapError(Exception):
    pass


class Map(object):
    """Base map object to configure a map. To define a map just subclass this.
    Attributes:
        name: The name of the map/class.
        players: Max number of players for this map
    """

    @property
    def name(self):
        return self.__class__.__name__
    
    @classmethod
    def all_subclasses(cls):
        """An iterator over all subclasses of `cls`."""
        for s in cls.__subclasses__():
            yield s
            for c in s.all_subclasses():
                yield c

def get_maps():
    """Get the full dict of maps {map_name: map_class}."""
    maps = {}
    for mp in Map.all_subclasses():
        if mp.__name__:
            map_name = mp.__name__
            if map_name in maps:
                raise DuplicateMapError("Duplicate map found: " + map_name)
            maps[map_name] = mp
    return maps

def get(map_name):
    """Get an instance of a map by name. Errors if the map doesn't exist."""
    if isinstance(map_name, Map):
        return map_name

    # Get the list of maps. This isn't at module scope to avoid problems of maps
    # being defined after this module is imported.
    maps = get_maps()
    map_class = maps.get(map_name)
    if map_class:
        return map_class()
    raise NoMapError("Map doesn't exist: %s" % map_name)