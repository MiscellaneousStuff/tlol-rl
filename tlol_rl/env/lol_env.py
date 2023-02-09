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
"""A League of Legends environment."""

from configparser import ConfigParser
import collections
from absl import logging

from tlol_rl import run_configs
from tlol_rl.env import environment


class Agent(collections.namedtuple("Agent", ["champ", "team"])):
    """Define an Agent. Each agent has a champion and which team it belongs to."""
    def __new__(cls, champion, team):
        return super(Agent, cls).__new__(cls, champion, team)


class LoLEnv(environment.Base):
    """A League of Legends environment.
    
    The implementation details ofthe action and observation specs
    are in lib/features.py
    """
    def __init__(self,
                 players=None,
                 map_name=None,
                 config_path=""):
        """Create a League of Legends environment.
        
        Args:
            map_name: Name of a League of Legends map. If non are chosen,
            this defaults to `Summoners Rift`.
            players: A list of Agent instances that specify who is playing.
            config_path: Path to configuration file containing directories
            as specified in README.md.
        """

        # Get and validate players
        if not players:
            raise ValueError("You must specify a list of players.")
        for p in players:
            if not isinstance(p, (Agent)):
                pass
        self.players = players

        # Assign number of agents
        self._num_agents = sum(1 for p in players if isinstance(p, Agent))

        # Assign map name
        if not map_name:
            raise ValueError("Missing a map name.")
        
        # Extract configuration directories
        try:
            with open(config_path) as f:
                cfg = ConfigParser()
                cfg.read_string(f.read())
                tlol_rl_server = cfg.get("dirs", "tlol_rl_server")
                logging.info("TLoL-RL Server (Directory): " + tlol_rl_server)
        except:
            raise IOError("Could not open config file: '%s'" % config_path)

        self._map_name = map_name
        self._run_config = run_configs.get(tlol_rl_server)
        self._game_info = None

        self._finalise()
    
    @property
    def map_name(self):
        """Get the current map name."""
        return self._map_name

    def action_spec(self):
        """Look at Features for full specs."""
        pass
    
    def observation_spec(self):
        """Look at Features for full specs."""
        pass
    
    def close(self):
        """Cleanly closes the environment by releasing/destroying
        resources which are no longer being used."""
        pass

    def reset(self):
        """Resets the current environment based on the initial
        state of the environment."""
        pass

    def step(self):
        """Takes one step in the environment. In the context
        of League of Legends, we can't fully control the environment
        so this is just an observation / action based on how many
        times we're taking observations and actions from the live
        running game."""
        pass

    def _finalise(self):
        logging.info("Environment is ready.")