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
import json


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

        self._last_obs = None

        # Accept custom client port, if provided
        self._kwargs["client_port"] = \
            self._kwargs["client_port"] \
                if "client_port" in kwargs else "5119"

        try:
            # Initialise Redis server
            logging.info("Initialising Redis.")
            arr = ["redis-server"]
            """,
                "redis.conf",
                "--bind", str(host),
                "--port", str(self._kwargs["redis_port"])]
            """
            logging.info("Redis Args: " + str(arr))
            self._redis_proc = subprocess.Popen(arr)

            # Initialise TLoL-RL Server
            logging.info("Initialising TLoL-RL Server.")
            tlol_rl_server_path = kwargs["tlol_rl_server_path"]
            tlol_arr = [tlol_rl_server_path]
            logging.info("TLoL-RL Server Args: " + str(arr))
            self._tlol_proc = subprocess.Popen(
                tlol_arr,
                cwd=kwargs["tlol_rl_server_dir"])
        except SubprocessError as e:
            logging.error("Could not open Redis. Error message: %s" % e)
    
    def close(self):
        """Kill the related processes when the controller is done."""
        self._redis_proc.kill()
        self._tlol_proc.kill()
    
    def connect(self):
        """Waits until this TLoL-RL instance can connect to a TLoL-RL server
        controller."""

        """
        # Wait until we can connect to the TLoL-RL Server
        json_txt = self.r.brpop("observation", self.timeout)
        if json_txt == None:
            logging.info("`client_join` == NONE")
            raise ConnectionError("Couldn't get `client_join` message from TLoL-RL Server")
        else:
            command = json.loads(json_txt[1].decode("utf-8"))
            if command == "clients_join":
                logging.info("`clients_join` == START CLIENT:" + str(command))
            else:
                logging.info("`clients_join` == WRONG MESSAGE: " + str(command))
                raise ConnectionError("Couldn't get `clients_join` message from TLoL-RL Server")

        # Clear all `client_join`` messages
        json_txt = self.r.brpop("observation", 1)
        cleared_all = False
        while not cleared_all:
            if json_txt != None:
                if json.loads(json_txt[1].decode("utf-8")) == "clients_join":
                    json_txt = self.r.brpop("observation", 1)
                else:
                    cleared_all = True
            else:
                cleared_all = True
        """
        
        # Reset pipes after connecting
        self.r.delete("observation") # Reset action pipe
        self.r.delete("action") # Reset action pipe

    def send_raw_action(self, action):
        """Send an action using the raw redis format."""
        print("action data:", action)

        action_type = action["action_type"]
        action_data = action["action_data"]

        self.r.lpush("action", action_type)
        self.r.lpush("action", action_data)
        
    def quit(self):
        """Shut down the redis process."""
        self.r = None
        self._redis_proc.kill()
        self._tlol_proc.kill()

    def players_reset(self):
        """Reset players for a new episode."""
        logging.info("Resetting players for new episode.")

        self.r.lpush("action", "reset")
        self.r.lpush("action", "")

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
    
    def observe(self):
        """Get a current observation."""
        
        # Start observing if we haven't already
        if self._last_obs == None:
            logging.info("controller.observe->start_observing")
            self.r.delete("observation") # Reset observation pipe
            self.r.delete("command")
            self.r.lpush("command", "start_observing") # Start observing
        
        logging.info("controller.observe->blocking for next observation")
        json_txt = self.r.brpop("observation", self.timeout)
        if json_txt == None:
            print("Error: Observation timed out")
            return None
        else:
            obs = json.loads(json_txt[1].decode("utf-8"))
            
            # Print first observation for testing...
            if self._last_obs == None: print("FIRST OBSERVATION:", obs)
            else:                      print("MID   OBSERVATION:", obs)
            
            self._last_obs = obs
            return obs
    
    def actions(self, req_action):
        """Send an action request, which may include multiple actions."""
        for action in req_action.actions:
            action = action.props
            if action["type"] == "no_op":
                self.player_noop()
            elif action["type"] == "move":
                x = action["move_range"].x - 4
                y = action["move_range"].y - 4
                print("SENDING MOVE COMMAND:", x, y)
                self.player_move(x, y)
            elif action["type"] == "spell":
                spell_slot = action["spell"]
                x = action["position"].x
                y = action["position"].y
                print("SENDING SPELL COMMAND:", spell_slot, x, y)
                self.player_spell(spell_slot, x, y)
        
    def act(self, action):
        """Send a single action. This is a shortcut for `actions`."""
        if action:
            return self.actions(action)
    
    def player_noop(self, n=1):
        for _ in range(n):
            self.r.lpush("action", "noop")
            self.r.lpush("action", "")
        return {"type": "noop", "data": ""}
    
    def player_move(self, x, y):
        action = {
            "x": float(x * 100.0),
            "y": float(y * 100.0)
        }
        self.r.lpush("action", "move")
        self.r.lpush("action", json.dumps(action))
        return {"type": "move", "data": action}
    
    def player_spell(self, spell_slot, x, y):
        action = {
            "spell_slot": int(spell_slot),
            "x": float(x * 1.0),
            "y": float(y * 1.0)
        }
        self.r.lpush("action", "spell")
        self.r.lpush("action", json.dumps(action))
        return {"type": "spell", "data": action}