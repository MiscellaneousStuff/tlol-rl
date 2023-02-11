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
"""Example of a basic full game environment with no actions."""

import gym
from absl import flags
from tlol_rl.lib import actions

import tlol_rl.envs

from absl import logging
from absl import flags
from absl import app

FLAGS = flags.FLAGS
flags.DEFINE_string("config_path", "./config.txt",
    "File containing directories of GameServer, League client respectively")
flags.DEFINE_string("host", "localhost", "IP Host of Redis")
flags.DEFINE_integer("redis_port", 6379, "IP Port of Redis")
flags.DEFINE_integer("max_episodes", 0, "Maximum number of episodes to run")
flags.DEFINE_integer("max_steps", 0, "Maximum number of steps to run")
flags.DEFINE_string("map", "Summoners Rift", "Name of league map to use.")
flags.DEFINE_string("champion", None, "Champion for agent to play.")

flags.mark_flag_as_required("champion")

_NO_OP = [actions.FUNCTIONS.no_op.id]

def main(unused_argv):
    env = gym.make("LoLGame-v0")
    env.settings["host"]        = FLAGS.host
    env.settings["redis_port"]  = FLAGS.redis_port
    env.settings["map_name"]    = FLAGS.map
    env.settings["champion"]    = FLAGS.champion
    env.settings["config_path"] = FLAGS.config_path

    obs_n = env.reset()

    for step in range(10000):
        action = [_NO_OP] * env.n_agents
        obs_n, reward_n, done_n, _ = env.step(action)
        logging.info("Step, Reward: " + str(step+1) + "," + str(reward_n))
        if any(done_n):
            break

    env.close()

if __name__ == "__main__":
    app.run(main)