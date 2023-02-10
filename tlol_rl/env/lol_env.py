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

import enum

from configparser import ConfigParser
import collections
from absl import logging
from pathlib import Path

from tlol_rl import run_configs
from tlol_rl.env import environment
from tlol_rl.lib.lcu import LCU
from tlol_rl.lib import features
from tlol_rl.lib import common

def to_list(arg):
    return arg if isinstance(arg, list) else [arg]

class Team(enum.IntEnum):
    BLUE = 0
    PURPLE = 1
    NEUTRAL = 2

def get_champ_ids():
    champ_ids = {}
    with open(Path(__file__).parent / "./champ_ids.txt") as f:
        for ln in f.read().split("\n"):
            id, champ = ln.split(": ")
            champ_ids[champ] = int(id)
    return champ_ids


class Agent(collections.namedtuple("Agent", ["champ", "team"])):
    """Define an Agent. Each agent has a champion and which team it belongs to."""
    def __new__(cls, champion, team):
        return super(Agent, cls).__new__(cls, champion, team)


Dimensions = features.Dimensions
AgentInterfaceFormat = features.AgentInterfaceFormat
parse_agent_interface_format = features.parse_agent_interface_format


class LoLEnv(environment.Base):
    """A League of Legends environment.
    
    The implementation details ofthe action and observation specs
    are in lib/features.py
    """
    def __init__(self,
                 host=None,
                 redis_port=None,
                 players=None,
                 agent_interface_format=None,
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
                raise ValueError(
                    "Expected players to be of type Agent. Got: %s." % p)
        self.players = players

        # Validate agent interface format
        if agent_interface_format is None:
            raise ValueError("Please specify agent_interface_format.")
        self._agent_interface_format = agent_interface_format

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
                lol_client     = cfg.get("dirs", "lol_client")
                logging.info("TLoL-RL Server (Directory): " + tlol_rl_server)
                logging.info("League of Legends Client (Directory): " + lol_client)
        except:
            raise IOError("Could not open config file: '%s'" % config_path)

        # Store environment variables
        self._map_name   = map_name
        self._run_config = run_configs.get(lol_client, tlol_rl_server)
        self._game_info  = None
        self._lcu        = LCU(timeout=2)

        # Launch the client, create a custom game and join it
        self._launch_game(host=host,
                          redis_port=redis_port,
                          players=players,
                          map_name=map_name)
        self._create_join(players=players,
                          map_name=map_name)

        # Finalise RL related variables for the environment
        self._finalise()
    
    @property
    def map_name(self):
        """Get the current map name."""
        return self._map_name

    def observation_spec(self):
        """Look at Features for full specs."""
        return tuple(f.observation_spec() for f in self._features)

    def action_spec(self):
        """Look at Features for full specs."""
        return tuple(f.action_spec() for f in self._features)
    
    def close(self):
        """Cleanly closes the environment by releasing/destroying
        resources which are no longer being used."""
        pass

    def _restart(self):
        # Restart the TLoL-RL server controllers
        for c in self._controllers:
            c.restart()

    def reset(self):
        """Starts a new episode."""
        self._episode_steps = 0

        # No need to restart for the first episode
        if self._episode_count:
            self._restart()

        self._episode_count += 1

        self._controllers[0].players_reset()

        logging.info("Starting episode %s: on %s" % (self._episode_count, self._map_name))
        self._state = environment.StepType.FIRST

        return self._observe()
    
    def _get_observations(self):
        """Get the raw observations from the controllers and
        convert them into NumPy arrays."""
        logging.info("_get_observations request and transform")

        obs = [self._controllers[0].observe() for _ in self.players]
        agent_obs = [self._features[0].transform_obs(o) for o in obs]
        
        logging.info("_get_observations received")

        # Save last observation to calculate rewards
        self._last_agent_obs = self._agent_obs

        # Set new observations
        self._obs, self._agent_obs = obs, agent_obs

    def _observe(self):
        """Take the NumPy arrays from the raw observations and
        convert them into `TimeStep`s."""
        self._get_observations()

        reward = [0] * self._num_agents

        logging.info("_observe")

        ret_val = tuple(environment.TimeStep(
            step_type=self._state,
            reward=r,
            discount=1,
            observation=o
        ) for r, o in zip(reward, self._agent_obs))

        logging.info("_observe->ret_val: " + str(ret_val))

        return ret_val

    def _step(self):
        logging.info("_step")
        return self._observe()

    def step(self, actions):
        """Apply actions, step the world forward, and return observations.
        Args:
            actions: A list of actions meeting the action spec, one per agent, or a
                list per agent. Using a list allows multiple actions per frame, but
                will still check that they're valid, so disabling
                ensure_available actions is encouraged.
        
        Returns:
            A tuple of TimeStep namedtuples, one per agent."""

        logging.info("Current env._state: " + str(self._state))
        if self._state == environment.StepType.LAST:
            return self.reset()
        
        new_actions = []
        for _, a in zip(self._obs, actions):
            # print("CURRENT OBS ENV STEP:", o)
            new_actions.append(self._features[0].transform_action(a))

        logging.info("new_actions: " + str(new_actions))

        for c, a in zip(self._controllers, actions):
            c.actions(common.RequestAction(actions=new_actions))

        logging.info("post_actions")

        self._state = environment.StepType.MID

        _step = self._step()

        logging.info("_step (obs): " + str(_step))

        return _step

    def _create_join(self, **kwargs):
        """Create the custom game, and join it."""
        if not self._lcu.client_loaded():
            raise OSError("Could not find League of Legends client")
        else:
            # Initialise LCU with `remoting-auth-token` and `app-port`
            self._lcu.late_init()

            # Create custom game
            res = self._lcu.create_custom(title="TLoL-RL", map_id=11)
            if not res.status_code == 200:
                raise RuntimeError("Could not create custom game")

            # Add bots
            res = self._lcu.add_bot()
            if not res.status_code == 204:
                raise RuntimeError("Could not add bots to custom game")

            # Start champion select
            res = self._lcu.start_champ_select()
            print(res.status_code, res.text)
            if not res.status_code == 200:
                raise RuntimeError("Could not start champion select")
            
            # Select champion
            champ_ids = get_champ_ids()
            res = self._lcu.pick_champion(
                champ_id=champ_ids[kwargs["players"][0].champ]) # Aphelios
            if not res.status_code == 204:
                raise RuntimeError("Could not pick champion")

    def _finalise(self):
        # Init episode / step counts
        self._total_steps = 0
        self._episode_steps = 0
        self._episode_count = 0

        # Features
        self._features = [features.features_from_game_info(
            agent_interface_format=self._agent_interface_format
        )]

        # Init observations and environment state
        self._last_agent_obs = [None] * self._num_agents
        self._obs = [None] * self._num_agents
        self._agent_obs = [None] * self._num_agents
        self._state = environment.StepType.LAST

        logging.info("Environment is ready.")
    
    def _launch_game(self, **kwargs):
        """Either launch or attach to an existing game."""
        logging.info("Initialising/attaching a game")

        kwargs["host"] = kwargs["host"]
        kwargs["redis_port"] = kwargs["redis_port"]

        self._lol_procs   = [self._run_config.start(**kwargs)]
        self._controllers = [p.controller for p in self._lol_procs]