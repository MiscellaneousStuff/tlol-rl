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
"""A random agent for League of Legends."""

import numpy

import logging

from tlol_rl.agents import base_agent
from tlol_rl.lib import actions


class RandomAgent(base_agent.BaseAgent):
    """A random agent for League of Legends."""
    
    def step(self, obs):
        super(RandomAgent, self).step(obs)
        
        function_id = numpy.random.choice(
            obs.observation["available_actions"])        
        args = [[numpy.random.randint(0, size) for size in arg.sizes]
                for arg in self.action_spec[0].functions[function_id].args]  

        logging.info("function_id, args: " + str(function_id) + " " + str(args))
        return actions.FunctionCall(function_id, args)