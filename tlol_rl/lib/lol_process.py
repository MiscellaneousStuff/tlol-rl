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
"""Launch the game, or attach to an already running game and
set up communication."""

import os


class LoLProcess(object):
    """Either launch a game of League of Legends or attach to an already
    running game, initialise a controller and later, clean up the environment.
    
    This is best used from run_configs, which decides which version to run,
    and where to find it.
    """

    def __init__(self):
        """Launch the League of Legends process.
        Args: 
        """
        self.controller = None

    def launch(self):
        """Launch the process and return the process object."""
        pass
    
    def __enter__(self):
        return self.controller

    def __exit__(self, unused_exception_type, unused_exc_value, unused_traceback):
        self.close()

    def close(self):
        """(Optionally) Shut down the game and clean up."""
        pass
    
    def shutdown(self):
        """(Optionally) Shutdown the game."""
        pass
    
    def check_exists(self, exec_path):
        if not os.path.isfile(exec_path):
            raise RuntimeError("Trying to run: '%s', but it doesn't exist " % exec_path)
        if not os.access(exec_path, os.X_OK):
            raise RuntimeError("Trying to run: '%s', but it isn't executable" % exec_path)