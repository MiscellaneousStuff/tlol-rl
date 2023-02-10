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

    def __init__(self,
                 riot_client_dir,
                 riot_client_name,
                 tlol_rl_server_dir,
                 tlol_rl_server_name,
                 riot_client_cwd=None,
                 tlol_rl_server_cwd=None,
                 env=None):
        # Riot Client
        riot_client_dir = os.path.expanduser(riot_client_dir)
        self.riot_client_dir = riot_client_dir
        self.riot_client_name = riot_client_name
        riot_client_cwd = \
            riot_client_cwd and os.path.join(riot_client_dir, riot_client_cwd)

        # TLoL-RL Server
        tlol_rl_server_dir = os.path.expanduser(tlol_rl_server_dir)
        self.tlol_rl_server_dir = tlol_rl_server_dir
        self.tlol_rl_server_name = tlol_rl_server_name
        tlol_rl_server_cwd = \
            tlol_rl_server_cwd and os.path.join(tlol_rl_server_dir, tlol_rl_server_cwd)

        super(LocalBase, self).__init__(
            riot_client_cwd=riot_client_cwd,
            tlol_rl_server_cwd=tlol_rl_server_cwd,
            env=env)
        
    def start(self, **kwargs):
        """Launch the game, or attach to an existing game."""
        logging.info("LocalBase kwargs: " + str(kwargs))

        # Riot Client Validation
        if not os.path.isdir(self.riot_client_dir):
            raise lol_process.LoLLaunchError(
                "Failed to run Riot Client binary at '%s" % self.riot_client_dir)
        riot_client_exec_path = \
            Path(os.path.expanduser(self.riot_client_dir)) / self.riot_client_name
        if not os.path.exists(riot_client_exec_path):
            raise lol_process.LoLLaunchError("No Riot Client binary found at: %s" % riot_client_exec_path)
        
        # TLoL-RL Server Validation
        if not os.path.isdir(self.tlol_rl_server_dir):
            raise lol_process.LoLLaunchError(
                "Failed to run TLoL-RL Server binary at '%s" % self.tlol_rl_server_dir)
        tlol_rl_server_path = \
            Path(os.path.expanduser(self.tlol_rl_server_dir)) / self.tlol_rl_server_name
        if not os.path.exists(tlol_rl_server_path):
            raise lol_process.LoLLaunchError("No TLoL-RL Server binary found at: %s" % tlol_rl_server_path)
        
        kwargs["tlol_rl_server_dir"] = self.tlol_rl_server_dir
        return lol_process.LoLProcess(
            self,
            riot_client_exec_path=riot_client_exec_path,
            tlol_rl_server_path=tlol_rl_server_path,
            **kwargs)


class Windows(LocalBase):
    """Run on windows."""
    def __init__(self, riot_client_dir, tlol_rl_server_dir):
        super(Windows, self).__init__(
            riot_client_dir=riot_client_dir,
            riot_client_name="LeagueClient.exe",
            tlol_rl_server_dir=tlol_rl_server_dir,
            tlol_rl_server_name="ConsoleApplication.exe",
            riot_client_cwd=riot_client_dir,
            tlol_rl_server_cwd=tlol_rl_server_dir)

    @classmethod
    def priority(cls):
        if platform.system() == "Windows":
            return 1
    
    def start(self, **kwargs):
        return super(Windows, self).start(**kwargs)