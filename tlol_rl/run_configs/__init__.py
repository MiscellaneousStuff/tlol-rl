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

from absl import logging

from tlol_rl.lib import lol_process
from tlol_rl.run_configs import lib
from tlol_rl.run_configs import platforms

def get(riot_client_dir, tlol_server_dir):
    """Get the config chosen by flags."""
    configs = {c.name(): c
        for c in lib.RunConfig.all_subclasses() if c.priority()}
    
    logging.info("List of run configs: " + ",".join([c for c in configs]))

    if not configs:
        raise lol_process.LoLLaunchError("No valid run_configs found.")
    
    return max(configs.values(), key=lambda c: c.priority())(
        riot_client_dir, tlol_server_dir)