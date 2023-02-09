# MIT License
# 
# Copyright (c) 2023MiscellaneousStuff
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
"""Run an agent."""

from absl import flags
from absl import app

from tlol_rl.agents import base_agent
from tlol_rl.env import lol_env
from tlol_rl.env import run_loop

FLAGS = flags.FLAGS
flags.DEFINE_string("host", "localhost", "IP Host of Redis")
flags.DEFINE_integer("redis_port", 6379, "IP Port of Redis")
flags.DEFINE_integer("max_episodes", 0, "Maximum number of episodes to run")
flags.DEFINE_integer("max_steps", 0, "Maximum number of steps to run")
flags.DEFINE_string("config_path", "./config.txt",
    "File containing directories of GameServer, League client respectively")
flags.DEFINE_string("map", "Summoners Rift", "Name of league map to use.")
flags.DEFINE_string("champion", None, "Champion for agent to play.")

flags.mark_flag_as_required("champion")

def main(unused_argv):
    agents  = [base_agent.BaseAgent()]
    players = [lol_env.Agent(champion=FLAGS.champion, team="BLUE")]

    with lol_env.LoLEnv(
        host=FLAGS.host,
        redis_port=FLAGS.redis_port,
        players=players,
        map_name=FLAGS.map,
        config_path=FLAGS.config_path) as env:
        
        run_loop.run_loop(agents, env)

if __name__ == "__main__":
    app.run(main)