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
"""Controllers take actions and generate observations."""

from absl import logging
import subprocess
from subprocess import SubprocessError


class ConnectError(Exception):
    pass


class RemoteController(object):
    """Implements a python interface to interact with a League of Legends client.

    All of these are implemented as blocking calls, so wait for the response
    before returning.
    """

    def __init__(self, proc=None, **kwargs):
        self._kwargs = kwargs

        try:
            logging.info("Initialise controller here")
        except SubprocessError as e:
            logging.error("Failed to initialise controller. Error message: %s" % e)
    
    def close(self):
        """Kill the related processes when the controller is done."""
        pass
    
    def connect(self):
        """Handle the process for the controller connecting to the server which
        is executing actions and returning observations."""
        pass

    def observe(self):
        """Get a current observation."""
        pass

    def act(self, action):
        """Send a single action."""
        pass
        
    def quit(self):
        """Shut down the controller process."""
        pass

    # """Implement player actions and observations here..."""

    def restart(self):
        """Restart the controller. This will either restart the game
        or just close a connection to an existing game."""

    def save_replay(self):
        """NOTE: TBD. This feature could include using TLoL to convert
        the game which has been played by the agent into a replay file
        which can be used for Data Analysis / ML development later
        down the line. This would use `tlol-py` to create the datasets
        from the .rofl files."""
        pass