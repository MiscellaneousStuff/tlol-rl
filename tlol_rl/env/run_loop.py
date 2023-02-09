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
"""A run loop for agent/environment interaction."""

from absl import logging
import time

def run_loop(agents, env, max_steps=0, max_episodes=0):
    # Connect
    controller = env._controllers[0]
    controller.connect()

    # A run loop for agent/environment interaction
    total_episodes = 0
    steps = 0
    start_time = time.time()

    # Obs / Act Specs
    observation_spec = [env.observation_spec() for _ in agents]
    action_spec = [env.action_spec() for _ in agents]

    # Agent Initialisation
    for agent, obs_spec, act_spec in zip(agents, observation_spec, action_spec):
        agent.setup(obs_spec, act_spec)
    
    try:
        while not max_episodes or total_episodes < max_episodes:
            total_episodes += 1
            timesteps = env.reset()
            
            for a in agents:
                a.reset()
            while True:
                steps += 1
                if max_steps and steps > max_steps: # +1 for initial reset action
                    return
                logging.info("run_loop->step: " + str(steps))
                actions = [agent.step(timestep)
                           for agent, timestep in zip(agents, timesteps)]
                
                if timesteps[0].last():
                    break
                
                timesteps = env.step(actions)
    except KeyboardInterrupt:
        pass
    finally:
        elapsed_time = (time.time() - start_time) + 1e-9 # NOTE: Make sure it's never 0
        print("Took %.3f seconds for %s steps: %.3f fps" % (
            elapsed_time, steps-1, (steps-1) / elapsed_time))