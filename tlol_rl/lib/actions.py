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
"""Define the static list of types and actions for League of Legends."""

import collections
import numbers
import enum
import numpy
import six

from tlol_rl.lib import point

def no_op(action, **kwargs):
    action.fill("no_op", **kwargs)

def move(action, **kwargs):
    action.fill("move", **kwargs)

def spell(action, **kwargs):
    action.fill("spell", **kwargs)

def numpy_to_python(val):
    """Convert numpy types to their corresponding python types."""
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, six.string_types):
        return val
    if (isinstance(val, numpy.number) or
        isinstance(val, numpy.ndarray) and not val.shape):  # numpy.array(1)
        return val.item()
    if isinstance(val, (list, tuple, numpy.ndarray)):
        return [numpy_to_python(v) for v in val]
    raise ValueError("Unknown value. Type: %s, repr: %s" % (type(val), repr(val)))

SPELL_FUNCTIONS = {}

always = lambda _: True

class ArgumentType(collections.namedtuple(
    "ArgumentType", ["id", "name", "sizes", "fn", "values"])):
    """Represents a single argument type.
    Attributes:
        id: The argument id. This is unique.
        name: The name of the argument, also unique.
        sizes: The max+1 of each of the dimensions this argument takes.
        fn: ...
        values: An enum representing the values this argument type could hold. None
            if this isn't an enum argument type.
    """
    __slots__ = ()

    def __str__(self):
        return "%s/%s %s" % (self.id, self.name, list(self.sizes))

    def __reduce__(self):
        return self.__class__, tuple(self)
        
    @classmethod
    def enum(cls, options, values):
        """Create an ArgumentType where you choose one of a set of known values."""
        names, real = zip(*options)
        del names  # unused

        def factory(i, name):
            return cls(i, name, (len(real),), lambda a: real[a[0]], values)
        return factory

    @classmethod
    def scalar(cls, value):
        """Create an ArgumentType with a single scalar in range(value)."""
        return lambda i, name: cls(i, name, (value,), lambda a: a[0], None)

    @classmethod
    def point(cls):  # No range because it's unknown at this time.
        """Create an ArgumentType that is represented by a point.Point."""
        def factory(i, name):
            return cls(i, name, (0, 0), lambda a: point.Point(*a).floor(), None)
        return factory

    @classmethod
    def spec(cls, id_, name, sizes):
        """Create an ArgumentType to be used in ValidActions."""
        return cls(id_, name, sizes, None, None)
        
class Arguments(collections.namedtuple("Arguments",
                ["move_range", "position", "spell"])):
    """The full list of argument types.
    Attributes:
        move_range: Relative units away from current position in 100s of units.
        position: A point on the map.
        spell: A champion ability or summoner spell cast by a champion.
    """
    __slots__ = ()

    @classmethod
    def types(cls, **kwargs):
        #Create an Arguments of the possible Types.#
        named = {name: factory(Arguments._fields.index(name), name)
                 for name, factory in six.iteritems(kwargs)}
        return cls(**named)
    
    def __reduce__(self):
        return self.__class__, tuple(self)

SPELL_OPTIONS = (
    ("Q", 0),
    ("W", 1),
    ("E", 2),
    ("R", 3),
    ("Sum1", 4),
    ("Sum2", 5)
)
Spell = ("Spell", SPELL_OPTIONS)

# List of types.
TYPES = Arguments.types(
    position=ArgumentType.point(),
    move_range=ArgumentType.point(),
    spell=ArgumentType.enum(SPELL_OPTIONS, Spell)
)

# Argument types for different functions.
FUNCTION_TYPES = {
    no_op: [],
    move: [TYPES.move_range],
    spell: [TYPES.spell, TYPES.position]
}

POINT_REQUIRED_FUNCS = {
    False: {},
    True: {move, spell}}

class Function(collections.namedtuple(
    "Function", ["id", "name", "function_type", "args", "avail_fn"])):
    """Represents a function action.
    
    Attributes:
        id: The function id, which is what the agent will use.
        name: The name of the function. Should be unique.
        function_type: One of the functions in FUNCTION_TYPES for how to construct
            the lol action out of python types.
        args: A list of the types of args passed to function_type.
        avail_fn: Returns whether the function is available.
    """
    __slots__ = ()

    @classmethod
    def no_op(cls, id_, name, function_type, avail_fn=always):
        return cls(id_, name, function_type, FUNCTION_TYPES[function_type], avail_fn)
    
    @classmethod
    def move(cls, id_, name, function_type, avail_fn=always):
        return cls(id_, name, function_type, FUNCTION_TYPES[function_type], avail_fn)

    @classmethod
    def spell(cls, id_, name, function_type, avail_fn=always):
        return cls(id_, name, function_type, FUNCTION_TYPES[function_type], avail_fn)

    """
    @classmethod
    def spell_ability(cls, id_, name, function_type, args, avail_fn):
        assert function_type in SPELL_FUNCTIONS
        return cls(id_, name, function_type, args, avail_fn)
    """

    @classmethod
    def spec(cls, id_, name, args):
        """Create a Function to be used in ValidActions."""
        return cls(id_, name, None, args, None)

    def __hash__(self):
        return self.id

    def __str__(self):
        return self.str()

    def __reduce__(self):
        return self.__class__, tuple(self)
    
    def __call__(self, *args):
        """A convenient way to create a FunctionCall from this Function."""
        print("This is being called")
        return FunctionCall.init_with_validation(self.id, args)

    def str(self, space=False):
        """String version. Set space=True to line them all up nicely."""
        return "%s/%s (%s)" % (str(int(self.id)).rjust(space and 4),
                            self.name.ljust(space and 50),
                            "; ".join(str(a) for a in self.args))

class Functions(object):
    """Represents the full set of functions.
    Can't use namedtuple since python3 has a limit of 255 function arguments, so
    build something similar.
    """

    def __init__(self, functions):
        functions = sorted(functions, key=lambda f: f.id)
        self._func_list = functions
        self._func_dict = {f.name: f for f in functions}
        if len(self._func_dict) != len(self._func_list):
            raise ValueError("Function names must be unique.")
    
    
    def __getattr__(self, name):
        return self._func_dict[name]

    def __getitem__(self, key):
        if isinstance(key, numbers.Integral):
            return self._func_list[key]
        return self._func_dict[key]

    def __getstate__(self):
        return self._func_list

    def __setstate__(self, functions):
        self.__init__(functions)

    def __iter__(self):
        return iter(self._func_list)

    def __len__(self):
        return len(self._func_list)

    def __eq__(self, other):
        return self._func_list == other._func_list

_FUNCTIONS = [
    Function.no_op(0, "no_op", no_op),
    Function.move(1, "move", move),
    Function.spell(2, "spell", spell)
]

# Create IntEnum of function names/ids so printing the id will show something useful.
# print("_FUNCTIONS := ", _FUNCTIONS)
_Functions = enum.IntEnum("_Functions", {f.name: f.id for f in _FUNCTIONS})
_FUNCTIONS = [f._replace(id=_Functions(f.id)) for f in _FUNCTIONS]
FUNCTIONS = Functions(_FUNCTIONS)

# Some indexes to support features.py and action conversion.
FUNCTIONS_AVAILABLE = {f.id: f for f in FUNCTIONS if f.avail_fn}

class FunctionCall(collections.namedtuple(
    "FunctionCall", ["function", "arguments"])):
    """Represents a function call action.
    Attributes:
        function: Store the function id.
        arguments: The list of arguments for that function, each being a list of
            ints.
    """
    __slots__ = ()

    @classmethod
    def init_with_validation(cls, function, arguments, raw=False):
        """Return a `FunctionCall` given some validation for the function and args.
        Args:
            function: A function name or id, to be converted into a function id enum.
            arguments: An iterable of function arguments. Arguments that are enum
                types can be passed by name. Arguments that only take on value (ie
                not a point) don't need to be wrapped in a list.
            raw: Whether this is a raw function call.
        Returns:
            A new `FunctionCall` instance.
        
        Raises:
            KeyError: if the enum doesn't exist.
            ValueError: if the enum id doesn't exist.
        """
        func = FUNCTIONS[function]
        args = []
        for arg, arg_type in zip(arguments, func.args):
            arg = numpy_to_python(arg)
            if arg_type.values: # Allow enum values by name or int.
                if isinstance(arg, six.string_types):
                    try:
                        args.append([arg_type.values[arg]])
                    except KeyError:
                        raise KeyError("Unknown argument value: %s, valid values: %s" % (
                            arg, [v.name for v in arg_type.values]))
                else:
                    if isinstance(arg, list):
                        arg = arg[0]
                    try:
                        args.append([arg_type.values[arg]])
                    except ValueError:
                        raise ValueError("Unknown argument value: %s, valid values: %s" % (
                arg, list(arg_type.values)))
            elif isinstance(arg, int): # Allow bare ints
                args.append([arg])
            elif isinstance(arg, list):
                args.append(arg)
            else:
                raise ValueError(
                    "Unknown argument value type: %s, expected int or list of ints, or "
                    "their numpy equivalents. Value: %s" % (type(arg), arg))
        print("FunctionCall: ", func.id, args)
        return cls(func.id, args)

    @classmethod
    def all_arguments(cls, function, arguments, raw=False):
        """Helper function for creating `FunctionCall`s with `Arguments`.
        Args:
        function: The value to store for the action function.
        arguments: The values to store for the arguments of the action. Can either
            be an `Arguments` object, a `dict`, or an iterable. If a `dict` or an
            iterable is provided, the values will be unpacked into an `Arguments`
            object.
        raw: Whether this is a raw function call.
        Returns:
        A new `FunctionCall` instance.
        """
        args_type = Arguments

        if isinstance(arguments, dict):
            arguments = args_type(**arguments)
        elif not isinstance(arguments, args_type):
            arguments = args_type(*arguments)
        return cls(function, arguments)
        
    def __reduce__(self):
        return self.__class__, tuple(self)

class ValidActions(collections.namedtuple(
    "ValidActions", ["types", "functions"])):
    """The set of types and functions that are valid for an agent to use.
    Attributes:
        types: A namedtuple of the types that the functions require. Unlike TYPES
            above, this include the sizes for screen.
        functions: A namedtuple of all the functions.
    """
    __slots__ = ()

    def __reduce__(self):
        return self.__class__, tuple(self)