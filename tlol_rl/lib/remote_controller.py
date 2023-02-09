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

import redis


class ConnectError(Exception):
    pass


class RequestError(Exception):
    def __init__(self, desc, res):
        super(RequestError, self).__init__(desc)
        self.res = res


class RemoteController(object):
    """Implements a python interface to interact with a League of Legends client.

    Will use Redis for now, may change to gRPC interface in the future.

    All of these are implemented as blocking calls, so wait for the response
    before returning.
    """

    def __init__(self, host, port, timeout_seconds, kwargs=[]):
        self._kwargs = kwargs

        # Initialise client connection to a Redis server
        timeout_seconds = timeout_seconds # or FLAGS.lol_timeout
        host = host or "192.168.0.16"
        port = port or 6379
        self.host = host
        self.port = port
        logging.info("Redis IP: " + str(host) + ":" + str(self._kwargs["redis_port"]))
        self.pool = redis.ConnectionPool(host=host, port=self._kwargs["redis_port"], db=0)
        self.r = redis.Redis(connection_pool=self.pool)
        self.timeout = timeout_seconds        
        self._client = None

        # Accept custom client port, if provided
        self._kwargs["client_port"] = \
            self._kwargs["client_port"] \
                if "client_port" in kwargs else "5119"

        try:
            logging.info("Initialising Redis.")
            arr = ["redis-server",
                "--bind", str(host),
                "--port", str(self._kwargs["redis_port"])]
            self._proc = subprocess.Popen(arr)
        except SubprocessError as e:
            logging.error("Could not open Redis. Error message: %s" % e)
    
    def close(self):
        """Kill the related processes when the controller is done."""
        self._proc.kill()
    
    def connect(self):
        """Waits until clients can join the TLoL-RL server then
        waits until agents can connect."""
        pass

    def observe(self):
        """Get a current observation."""
        pass

    def act(self, action):
        """Send a single action."""
        pass
        
    def quit(self):
        """Shut down the redis process."""
        self.r = None
        self._proc.kill()

    # """Implement player actions and observations here..."""

    def restart(self):
        """Restart the controller. This will either restart the game
        or just close a connection to an existing game."""
        pass

    def save_replay(self):
        """NOTE: TBD. This feature could include using TLoL to convert
        the game which has been played by the agent into a replay file
        which can be used for Data Analysis / ML development later
        down the line. This would use `tlol-py` to create the datasets
        from the .rofl files."""
        pass