# MIT License
# 
# Copyright (c) 2020 MiscellaneousStuff
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
"""Full League of Legends 1v1 environment."""

import logging
import numpy as np

import gym
from gym.spaces import Box

from tlol_rl.env import lol_env
from tlol_rl.env.environment import StepType
from tlol_rl.lib import actions

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_NO_OP = actions.FUNCTIONS.no_op.id

class LoLGameEnv(gym.Env):
    default_settings = {
        'agent_interface_format': \
            lol_env.parse_agent_interface_format(
            feature_map=16000,
            feature_move_range=8),
    }

    def __init__(self, **kwargs) -> None:
        super().__init__()

        self.observation_space = Box(low=0, high=1, shape=(1,), dtype=np.float32)
        self.action_space      = Box(low=0, high=1, shape=(1,), dtype=np.float32)

        self._kwargs = kwargs
        self._env = None

        self.n_agents = 1

        self._episode = 0
        self._num_step = 0
        self._episode_reward = [0.0] * self.n_agents
        self._total_reward = [0.0] * self.n_agents

    def step(self, actions):
        return self._safe_step(actions)

    def _safe_step(self, acts):
        self._num_step += 1
        try:
            cur_actions = [actions.FunctionCall(act[0], act[1:])
                           for act in acts]
            obs_n = self._env.step(cur_actions)
        except KeyboardInterrupt:
            logger.info(" Interrupted. Quitting...")
            return [None] * self.n_agents, [0] * self.n_agents, [True] * self.n_agents, \
                [{}] * self.n_agents
        except Exception:
            logger.exception(" An unexpected error occurred while applying action to environment.")
            return [None] * self.n_agents, [0] * self.n_agents, [True] * self.n_agents, \
                [{}] * self.n_agents
        reward_n = [obs.reward for obs in obs_n]
        self._episode_reward = [self._episode_reward[i] + reward_n[i] for i in range(self.n_agents)]
        self._total_reward = [self._total_reward[i] + reward_n[i] for i in range(self.n_agents)]
        done_n = [obs.step_type == StepType.LAST for obs in obs_n]
        return obs_n, reward_n, done_n, {}

    def reset(self):
        logger.info("Resetting LoLEnv")
        if self._env is None:
            self._init_env()
        if self._episode > 0:
            mean_reward = [float(total_reward) / self._episode
                           for total_reward in self._total_reward]
            logger.info(" Episode {0} ended with reward {1} after {2} steps.".format(
                        self._episode, self._episode_reward, self._num_step))
            logger.info(" Got {0} total reward, with an average reward of {1} per episode".format(
                        self._total_reward, mean_reward))
        self._episode += 1
        self._num_step = 0
        self._episode_reward = [0.0] * self.n_agents
        logger.info(" Episode %d starting...", self._episode)
        obs = self._env.reset()
        # self.available_actions = obs.observation['available_actions']
        return obs

    def _init_env(self):
        args = {**self.default_settings, **self._kwargs}
        args["players"] = [lol_env.Agent(champion=args["champion"], team="BLUE")]
        if "champion" in args: del args["champion"]

        logger.debug("Intialize LoLEnv with settings: %s", args)

        # Setup environment
        self._env = lol_env.LoLEnv(**args)

        # Connect to the game after setting up the environment
        controller = self._env._controllers[0]
        controller.connect()

    def close(self):
        logging.info("Closing LoLEnv")
        if self._episode > 0:
            mean_reward = [float(total_reward) / self._episode
                           for total_reward in self._total_reward]
            logger.info(" Episode {0} ended with reward {1} after {2} steps.".format(
                        self._episode, self._episode_reward, self._num_step))
            logger.info(" Got {0} total reward, with an average reward of {1} per episode".format(
                        self._total_reward, mean_reward))
        if self._env is not None:
            self._env.close()
        super().close()
        
    @property
    def settings(self):
        return self._kwargs

    @property
    def action_spec(self):
        if self._env is None:
            self._init_env()
        return self._env.action_spec()

    @property
    def observation_spec(self):
        if self._env is None:
            self._init_env()
        return self._env.observation_spec()

    @property
    def episode(self):
        return self._episode

    @property
    def num_step(self):
        return self._num_step

    @property
    def episode_reward(self):
        return self._episode_reward

    @property
    def total_reward(self):
        return self._total_reward