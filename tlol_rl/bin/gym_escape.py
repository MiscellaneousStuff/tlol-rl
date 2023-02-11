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
"""Example of a basic full game environment implementing PPO.

Runs the `Escape1DEnv` environment which trains the agent to go the
opposite direction of the enemy agent by clicking away or using spells."""

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

def main(unused_argv):
    pass

if __name__ == "__main__":
    app.run(main)