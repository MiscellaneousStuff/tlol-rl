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
"""Python RL Environment API."""

import abc
import enum
import six


class StepType(enum.IntEnum):
    """Defines the status of a `TimeStep` within a sequence."""
    FIRST = 0
    MID = 1
    LAST = 2


@six.add_metaclass(abc.ABCMeta)
class Base(object):
    """Abstract base class for Python RL environments."""

    @abc.abstractmethod
    def reset(self):
        """Starts a new sequence and returns the first `TimeStep` of this sequence.
        Returns:
            A `TimeStep` namedtuple containing:
                step_type: A `StepType` of `FIRST`
                reward: Zero.
                discount: Zero.
                observation: A NumPy array, or a dict, list of tuple of arrays
                    corresponding to `observation_spec()`.
        """
    
    @abc.abstractmethod
    def step(self, action):
        """Updates the environment according to the action and returns a `TimeStep`.
        If the environment returned a `TimeStep` with `StepType.LAST` at the
        previous step, this call to `step` will start a new sequence and `action`
        will be ignored.
        Args:
            action: A NumPy array, or a dict, list or tuple of arrays corresponding to
                `action_spec()`.
        
        Returns:
            A `TimeStep` namedtuple containing:
                step_type: A `StepType` value.
                reward: Reward at this timestep.
                discount: A discount in the range [0, 1].
                observation: A NumPy array, or a dict, list or tuple of arrays
                    corresponding to `observation_spec()`.
        """

    @abc.abstractmethod
    def observation_spec(self):
        """Defines the observations provided by the environment.
        Returns:
            A tuple of specs(one per agent), where each spec is a dict of shape
            tuples.
        """
        pass

    @abc.abstractmethod
    def action_spec(self):
        """Defines the actions that should be provided to `step`.
        Returns:
            A tuple of specs (one per agent), where each spec is something that
            defines the shape of the actions.
        """
        pass

    @abc.abstractmethod
    def close(self):
        """Frees any resources used by the environment.
        Implment this method for an environment backed by an external process.
        This method can be used directly
        
        ```python
        env = Env(...)
        # Use env
        env.close()
        ```
        or via a context manager
        ```python
        with Env(...) as env:
            # Use env.
        ```
        """
        pass

    def __enter__(self):
        """Allows the environment to be used in a with-statement context."""
        return self
    
    def __exit__(self, unused_exception_type, unused_exc_value, unused_traceback):
        """Allows the environment to be used in a with-statement context."""
        self.close()
    
    def __del__(self):
        self.close()