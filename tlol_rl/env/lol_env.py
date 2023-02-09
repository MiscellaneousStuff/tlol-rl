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

from tlol_rl.env import environment


class LoLEnv(environment.Base):
    """A League of Legends environment.
    
    The implementation details ofthe action and observation specs
    are in lib/features.py
    """
    def __init__(self):
        pass

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