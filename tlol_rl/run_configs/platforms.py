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
"""Configs for how to run League of Legends on different platforms."""

from absl import logging
import os
import platform
from pathlib import Path

from tlol_rl.lib import lol_process
from tlol_rl.run_configs import lib


class LocalBase(lib.RunConfig):
    """Base run config for League of Legends installations."""

    def __init__(self, exec_dir, exec_name, cwd=None, env=None):
        exec_dir = os.path.expanduser(exec_dir)
        self.exec_dir = exec_dir
        self.exec_name = exec_name
        cwd = cwd and os.path.join(exec_dir, cwd)
        super(LocalBase, self).__init__(cwd=cwd, env=env)
        
    def start(self, **kwargs):
        """Launch the game, or attach to an existing game."""
        logging.info("LocalBase kwargs: " + str(kwargs))

        if not os.path.isdir(self.exec_dir):
            raise lol_process.LoLLaunchError(
                "Failed to run GameServer at '%s" % self.exec_dir)

        exec_path = Path(os.path.expanduser(self.exec_dir)) / self.exec_name

        if not os.path.exists(exec_path):
            raise lol_process.LoLLaunchError("No Riot Client binary found at: %s" % exec_path)
        
        return lol_process.LoLProcess(self, exec_path=exec_path, **kwargs)


class Windows(LocalBase):
    """Run on windows."""
    def __init__(self, exec_dir):
        super(Windows, self).__init__(exec_dir, "LeagueClient.exe", cwd=exec_dir)

    @classmethod
    def priority(cls):
        if platform.system() == "Windows":
            return 1
    
    def start(self, **kwargs):
        return super(Windows, self).start(**kwargs)