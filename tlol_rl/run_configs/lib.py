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
"""Configs for various ways of running a League of Legends RL agent."""

import os
import datetime
import uuid

Exists = os.path.exists
IsDirectory = os.path.isdir
ListDir = os.listdir
MakeDirs = os.makedirs
Open = open


class RunConfig(object):
    """Base class for different run configs."""

    def __init__(self, cwd=None, env=None):
        """Initialize the runconfig with the various directories needed."""
        self.cwd = cwd
        self.env = env

    def start(self, **kwargs):
        raise NotImplementedError()
    
    @classmethod
    def priority(cls):
        """None means this isn't valid. Run the one with the max priority."""
        return None
        
    @classmethod
    def all_subclasses(cls):
        """An iterator over all subclasses of `cls`."""
        for s in cls.__subclasses__():
            yield s
            for c in s.all_subclasses():
                yield c
    
    @classmethod
    def name(cls):
        return cls.__name__

    def save_replay(self, replay_data, replay_dir, prefix=None):
        """Save a replay to a directory, returning the path to the replay.
        Args:
            replay_data: The result of controller.save_replay(), whch is a serialised
                list of the map, players, multiplier and timestamped actions.
        
        Returns:
            The full path where the replay is saved.
        
        Raises:
            ValueError: If the prefix contains the path separator.
        """
        pass