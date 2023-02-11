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
"""Example of a basic full game environment implementing Proximal Policy
Optimisation (PPO).

Uses TLoL-RL without OpenAI Gym. The task is a simple one, the agent needs to
maximise it's distance from an enemy target dummy in a Practice Tool game.
However, it shows that the RL environment and PPO training is working properly."""

import time
import torch
import numpy as np

from absl import logging
from absl import flags
from absl import app

from tlol_rl.agents import ppo_agent
from tlol_rl.env    import lol_env
from tlol_rl.lib    import point_flag
from tlol_rl.lib    import ppo
from tlol_rl.lib    import point
from tlol_rl.lib    import actions

from gym.spaces import Box, Discrete

FLAGS = flags.FLAGS

# Agent Spec
point_flag.DEFINE_point("feature_map_size", "16000",
                        "Resolution for screen feature layers.")
point_flag.DEFINE_point("feature_move_range", "8",
                        "Resolution for screen feature layers.")

# Env Related
flags.DEFINE_string("host", "localhost", "IP Host of Redis")
flags.DEFINE_integer("redis_port", 6379, "IP Port of Redis")
flags.DEFINE_string("config_path", "./config.txt",
    "File containing directories of Riot Client, TLoL-RL Server, respectively")
flags.DEFINE_string("map", "Summoners Rift", "Name of league map to use.")
flags.DEFINE_string("champion", None, "Champion for agent to play.")

# PPO Related
flags.DEFINE_string("model_path",   "",   "PyTorch Model checkpoint")
flags.DEFINE_float("lr_actor",      3e-2, "Actor model learning rate")
flags.DEFINE_float("lr_critic",     1e-2, "Critic model learning rate")
flags.DEFINE_float("eps_clip",      0.2,  "PPO clipping rate")
flags.DEFINE_float("gamma",         0.99, "RL discount factor")
flags.DEFINE_integer("K_epochs",    1,    "Number of epochs to optimise policy")
flags.DEFINE_integer("epochs",      50,   "Total number of training epochs")
flags.DEFINE_integer("max_steps",   25,   "Maximum number of steps per episode")
flags.DEFINE_integer("random_seed", 1,    "Random seed for all libraries")

flags.mark_flag_as_required("champion")

def convert_action(act):
    act_x = 8 if act else 0
    act_y = 4
    return actions.FunctionCall(1, [point.Point(act_x, act_y)])

def get_obs(obs):
    me_pos    = point.Point(
        obs.observation["me_x"],
        obs.observation["me_y"])
    enemy_pos = point.Point(
        obs.observation["enemy_x"],
        obs.observation["enemy_y"])
    dist = me_pos.dist(enemy_pos)
    arr = np.array(dist)[None]
    return arr

def train(env, epochs, max_steps, lr_actor, lr_critic, device):
    # Connect
    controller = env._controllers[0]
    controller.connect()

    # A run loop for agent/environment interaction
    total_episodes = 0
    start_time     = time.time()
    
    eps_clip = FLAGS.eps_clip
    gamma    = FLAGS.gamma
    K_epochs = FLAGS.K_epochs # K_epochs = 1 # Originaly 80
    agent = ppo.PPO(
        Box(low=0, high=16000, shape=(1,), dtype=np.float32), # Obs Spec
        Discrete(2), # Act Spec
        lr_actor,
        lr_critic,
        gamma,
        K_epochs,
        eps_clip,
        device)

    # PPO Update Rate Variables
    update_step = max_steps * 1
    total_steps = 0

    try:
        while not epochs or total_episodes < epochs:
            steps          = 0            
            total_episodes += 1
            timesteps = env.reset()

            rews = []

            while True:
                steps += 1
                total_steps += 1

                # Exit if max steps
                if max_steps and steps > max_steps:
                    break
                
                # Get action for current obs
                obs = get_obs(timesteps[0])
                act = agent.act(obs)
                act = convert_action(act)

                # Get new obs
                timesteps = env.step([act])
                
                # Calculate reward
                rew = get_obs(timesteps[0])[0] / 1000.0
                rews.append(rew)

                # Saving reward and if terminal
                agent.buffer.rewards.append(rew)
                agent.buffer.is_terminals.append(timesteps[0].last())

                # Update PPO agent
                if total_steps % update_step == 0:
                    agent.update()
                    # agent.save(checkpoint_path)

                # Exit if terminal state
                if timesteps[0].last():
                    break
            
            logging.info("Episodes, reward: %d %f" % (total_episodes, sum(rews)))
            
    except KeyboardInterrupt:
        pass

    finally:
        elapsed_time = (time.time() - start_time) + 1e-9 # NOTE: Make sure it's never 0
        print("Took %.3f seconds for %s steps: %.3f fps" % (
            elapsed_time, steps-1, (steps-1) / elapsed_time))

def main(unused_argv):
    # Random seed
    random_seed = FLAGS.random_seed
    if random_seed:
        torch.manual_seed(random_seed)
        np.random.seed(random_seed)

    players = [lol_env.Agent(champion=FLAGS.champion, team="BLUE")]

    epochs    = FLAGS.epochs
    max_steps = FLAGS.max_steps
    lr_actor  = FLAGS.lr_actor
    lr_critic = FLAGS.lr_critic

    # Use GPU if available
    if (torch.cuda.is_available()):
        device = torch.device("cuda:0")
        torch.cuda.empty_cache()
        logging.info("Device set to: " + str(torch.cuda.get_device_name(device)))
    else:
        device = torch.device("cpu")
        logging.info("Device set to: CPU")

    with lol_env.LoLEnv(
        host=FLAGS.host,
        redis_port=FLAGS.redis_port,
        players=players,
        agent_interface_format=lol_env.parse_agent_interface_format(
            feature_map=FLAGS.feature_map_size,
            feature_move_range=FLAGS.feature_move_range),
        map_name=FLAGS.map,
        config_path=FLAGS.config_path) as env:

        train(env,
              epochs=epochs,
              max_steps=max_steps,
              lr_actor=lr_actor,
              lr_critic=lr_critic,
              device=device)

if __name__ == "__main__":
    app.run(main)