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
"""Convert TLoL-RL Server features into NumPy arrays."""

from absl import logging
import enum
import numpy as np

from tlol_rl.lib import named_array
from tlol_rl.lib import point
from tlol_rl.lib import actions
from tlol_rl.lib import common


class ChampUnit(enum.IntEnum):
    """Indices into the `ChampUnit` observation."""
    pass


class FeatureType(enum.Enum):
    SCALAR = 1
    CATEGORICAL = 2


class AgentInterfaceFormat(object):
    """Observation and action interface format specific to a particular agent."""
    
    def __init__(self, feature_dimensions=None):
        """Initializer.
        Args:
            feature_dimensions: Feature layer `Dimension`.
        """
        if not feature_dimensions:
            raise ValueError("Must set feature dimensions")
            
        self._feature_dimensions = feature_dimensions
        self._action_dimensions = feature_dimensions

    @property
    def feature_dimensions(self):
        return self._feature_dimensions
    
    @property
    def action_dimensions(self):
        return self._action_dimensions


def parse_agent_interface_format(feature_map=None, feature_move_range=None):
    """Creates an AgentInterfaceFormat object from keyword args.
    Convenient when using dictionaries or command-line arguments for config.
    Note that the feature_* and rgb_* properties define the respective spatial
    observation dimensions and accept:
        * None or 0 to disable that spatial observation.
        * A single int for a square observation with that side length.
        * A (int, int) tuple for a rectangular (width, height) observation.
    Args:
        feature_map: Map dimensions.
        feature_move_range: Range of movement (divided by 100) the agent can move.
    
    Returns:
        An `AgentInterfaceFormat` object.
    
    Raises:
    ValueError: If an invalid parameter is specified.
    """
    if feature_map and feature_move_range:
        feature_dimensions = Dimensions(feature_map,
            feature_move_range)
    
    return AgentInterfaceFormat(feature_dimensions=feature_dimensions)

def _to_point(dims):
  """Convert (width, height) or size -> point.Point."""
  assert dims

  if isinstance(dims, (tuple, list)):
    if len(dims) != 2:
      raise ValueError(
          "A two element tuple or list is expected here, got {}.".format(dims))
    else:
      width = int(dims[0])
      height = int(dims[1])
      if width <= 0 or height <= 0:
        raise ValueError("Must specify +ve dims, got {}.".format(dims))
      else:
        return point.Point(width, height)
  else:
    size = int(dims)
    if size <= 0:
      raise ValueError(
          "Must specify a +ve value for size, got {}.".format(dims))
    else:
      return point.Point(size, size)

class Dimensions(object):
    """Map dimensions configuration.
    Map dimensions must be specified. Sizes must be positive.
    Attributes:
        map: A (width, height) int tuple or a single int to be used.
        move_range: A (width, height) int tuple or a single int to be used.
    """

    def __init__(self, map=None, move_range=None):
        if not map:
            raise ValueError("map must be set, map={}".format(map))
            
        if not move_range:
            raise ValueError("move_range must be set, move_range={}".format(move_range))
    
        self._map = _to_point(map)
        self._move_range = _to_point(move_range)

    @property
    def map(self):
        return self._map
    
    @property
    def move_range(self):
        return self._move_range
    
    def __repr__(self):
        return "Dimensions(map={}, move_range={})".format(self._map, self._move_range)

    def __eq__(self, other):
        return (isinstance(other, Dimensions) and self._map == other._map and
                self._move_range == other._move_range)

    def __ne__(self, other):
        return not self == other


class Features(object):
    """Render feature layers from GameServer observation into numpy arrays."""

    def __init__(self, agent_interface_format=None):
        """Initialize a Features instance matching the specified interface format.
        Args:
            agent_interface_format: See the documentation for `AgentInterfaceFormat`.
        """
        if not agent_interface_format:
            raise ValueError("Please specify agent_interface_format")
        
        self._agent_interface_format = agent_interface_format
        aif = self._agent_interface_format

        self._valid_functions = _init_valid_functions(aif.action_dimensions)
    
    def observation_spec(self):
        """The observation spec for the League of Legends v4.20 environment.
        
        Returns:
            The dict of observation names 
        """

        aif = self._agent_interface_format

        obs_spec = named_array.NamedDict({
            "my_id": (0,),
            "game_time": (0,),
            "me_unit": (len(ChampUnit),),
            "enemy_unit": (len(ChampUnit),)
        })
        
        """
        if aif.feature_dimensions:
            obs_spec["feature_map"] = (len(MAP_FEATURES),
                                       aif.feature_dimensions.map.x,
                                       aif.feature_dimensions.map.y)
            obs_spec["feature_move_range"] = (len(MOVE_RANGE_FEATURES),
                                       aif.feature_dimensions.move_range.x,
                                       aif.feature_dimensions.move_range.y)
        """

        obs_spec["available_actions"] = (0,)

        return obs_spec

    def action_spec(self):
        """The action space pretty complicated and fills the ValidFunctions."""
        return self._valid_functions

    def available_actions(self, obs):
        """Return the list of available action ids."""
        available_actions = set()
        obs_available_actions = obs["available_actions"]
        # print("AVAILABLE ACTIONS:", obs_available_actions)
        if obs_available_actions["can_no_op"]: available_actions.add(0)
        if obs_available_actions["can_move"]: available_actions.add(1)
        if  obs_available_actions["can_spell_0"] or \
            obs_available_actions["can_spell_1"] or \
            obs_available_actions["can_spell_2"] or \
            obs_available_actions["can_spell_3"] or \
            obs_available_actions["can_spell_4"] or \
            obs_available_actions["can_spell_5"]:
            available_actions.add(2)
        
        return list(available_actions)

    def transform_action(self, func_call):
        """Transform an agent-style action to one that TLoL-RL Server can consume.
        Args:
            obs: an observation extracted from Redis from the previous step.
            func_call: a `FunctionCall` to be turned into a a redis action.
        
        Returns:
            a corresponding `common.Action`.
        
        Raises:
            ValueError: if the action doesn't pass validation.
        """

        """
        if isinstance(func_call, common.Action):
            return func_call
        """

        # Valid id?
        func_id = func_call.function
        try:
            func = actions.FUNCTIONS[func_id]
        except KeyError:
            raise ValueError("Invalid function: %s." % func_id)
            
        # Correct number of args?
        if len(func_call.arguments) != len(func.args):
            raise ValueError(
                "Wrong number of arguments for function: %s, got: %s" % (
                    func, func_call.arguments))
        
        # Args are valid?
        aif = self._agent_interface_format
        # print("FUNC:", func.args, func_call.arguments)
        for t, arg in zip(func.args, func_call.arguments):
            if t.name in ("position"):
                sizes = aif.action_dimensions.map
            elif t.name in ("move_range"):
                sizes = aif.action_dimensions.move_range
            else:
                sizes = t.sizes
            if len(sizes) != len(arg):
                raise ValueError(
                    "Wrong number of values for argument of %s, got: %s" % (
                        func, func_call.arguments))
            for s, a in zip(sizes, arg):
                if not np.all(0 <= a) and np.all(a < s):
                    raise ValueError("Argument is out of range for %s, got: %s" % (
                        func, func_call.arguments))

        # Convert them to python types
        kwargs = {type_.name: type_.fn(a)
              for type_, a in zip(func.args, func_call.arguments)}

        # redis magic...
        lol_action = common.Action()

        kwargs["action"] = lol_action
        actions.FUNCTIONS[func_id].function_type(**kwargs)

        return lol_action

    def transform_obs(self, obs):
        """Render some TLoL-RL Server observations into something an agent can handle."""

        # Print original observation
        logging.info("transform_obs().obs: " + str(obs))

        # Observation output
        out = named_array.NamedDict({
            "time":    float(obs["time"]),
            "me_x":    float(obs["self"]["pos_x"]),
            "me_y":    float(obs["self"]["pos_y"]),
            "enemy_x": float(obs["enemy_unit"]["pos_x"]),
            "enemy_y": float(obs["enemy_unit"]["pos_y"]),
        })

        # Set available actions
        out["available_actions"] = \
            np.array(
                self.available_actions(obs),
                dtype=np.int32)
        
        return out


def _init_valid_functions(action_dimensions):
    """Initialize ValidFunctions and set up the callbacks."""
    sizes = {
        "position": tuple(int(i) for i in action_dimensions.map),
        "move_range": tuple(int(i) for i in action_dimensions.move_range)
    }

    types = actions.Arguments(*[
        actions.ArgumentType.spec(t.id, t.name, sizes.get(t.name, t.sizes))
        for t in actions.TYPES])

    functions = actions.Functions([
        actions.Function.spec(f.id, f.name, tuple(types[t.id] for t in f.args))
        for f in actions.FUNCTIONS])
    
    return actions.ValidActions(types, functions)
    
def features_from_game_info(agent_interface_format=None):
    """Construct a Features object using data extracted from game info.
    Returns:
        A features object.
    """

    return Features(agent_interface_format=agent_interface_format)