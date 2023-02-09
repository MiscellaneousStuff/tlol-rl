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
"""Provides an interface to interact with a running League of Legends
client via the LCU api."""

from absl import logging

import base64
import requests
import json
import psutil
import uuid
import time

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LCU(object):
    def __init__(self, remoting_auth_token=None, app_port=None, timeout=0.5):
        """Initialises LCU API using either provided `remoting_auth_token`
        and `app_port` or tries to automatically find it from a running
        client.
        """
        self.remoting_auth_token = remoting_auth_token
        self.app_port = app_port
        self.timeout = timeout

    def late_init(self):
        """Allows initialising an LCU class without having an
        already running client. Useful if running the client
        asynchronously."""
        self.remoting_auth_token, self.app_port = \
            self.get_lcu_params()
    
    def request(self, suffix_url, method, data=None):
        """Sends a request to the LCU API."""
        
        time.sleep(self.timeout)

        # Auth and port
        auth_token = base64.b64encode(
            f"riot:{self.remoting_auth_token}".encode("utf-8"))
        auth_token = str(auth_token, encoding="utf-8")
        app_port = self.app_port
        url = f"https://127.0.0.1:{app_port}{suffix_url}"

        # Validate HTTP method
        if not method in ["get", "post", "patch"]:
            raise ValueError("Invalid HTTP method: " + url + " " + method)

        # Execute HTTP call and return data
        if method == "post":
            req = requests.post(
                url=url,
                headers={
                    "Authorization": f"Basic {auth_token}",
                    "Content-Type": "application/json"
                },
                data=json.dumps(data),
                verify=False)
        elif method == "patch":
            req = requests.patch(
                url=url,
                headers={
                    "Authorization": f"Basic {auth_token}",
                    "Content-Type": "application/json"
                },
                data=json.dumps(data),
                verify=False)
        elif method == "get":
            print("CUSTOM START:", url)
            req = requests.get(
                url=url,
                headers={
                    "Authorization": f"Basic {auth_token}",
                    "Content-Type": "application/json"
                },
                verify=False)
        return req

    def get_lcu_params(self):
        """Attempts to automatically acquire the `remoting_auth_token`
        and `app_port` from a running League of Legends client."""
        for proc in psutil.process_iter():
            try:
                n = proc.name()
                if n == "LeagueClientUx.exe":
                    cmdline = proc.cmdline()
                    port = None
                    tok = None
                    for arg in cmdline:
                        if "--app-port" in arg:
                            port = arg.split("=")[1]
                        elif "--remoting-auth-token" in arg:
                            tok = arg.split("=")[1]
                    return tok, port
            except:
                pass
        return None, None

    def create_custom(self, title):
        data = {
            "customGameLobby": {
                "configuration": {
                    "gameMode": "PRACTICETOOL",
                    "gameMutator": "",
                    "gameServerRegion": "",
                    "mapId": 11,
                    "mutators": {"id": 1},
                    "spectatorPolicy": "AllAllowed",
                    "teamSize": 5
                },
                "lobbyName": title,
                "lobbyPassword": str(uuid.uuid4())
            },
            "isCustom": True
        }
        res = self.request(
            suffix_url="/lol-lobby/v2/lobby",
            method="post",
            data=data)
        return res
    
    def add_bot(self, champ_id=3, difficulty="MEDIUM", team="200"):
        data = {
            "botDifficulty": difficulty,
            "championId": champ_id,
            "teamId": team
        }
        res = self.request(
            suffix_url="/lol-lobby/v1/lobby/custom/bots",
            method="post",
            data=data)
        return res

    def client_loaded(self, timeout=30):
        """Waits until the client is loaded. Tries
        until `timeout` number of seconds before giving up."""
        for tm in range(timeout):
            for proc in psutil.process_iter():
                try:
                    n = proc.name()
                    if n == "LeagueClientUx.exe":
                        return True
                except:
                    pass
            logging.info(
                "Waiting for League of Legends client for %d/%d seconds." %
                (tm, timeout))
            time.sleep(1)
        return False
    
    def start_champ_select(self):
        """Start champion selection process after creating a custom
        game."""
        res = self.request(
            suffix_url="/lol-lobby/v1/lobby/custom/start-champ-select",
            method="post")
        return res
    
    def pick_champion(self, champ_id):
        """Selects a champion to lock in during pick-phase."""
        """
        data = {
            "actorCellId": 0,
            "championId": 0,
            "completed": True,
            "id": champ_id,
            "isAllyAction": True,
            "type": "string"
        }
        
        res = self.request(
            suffix_url="/lol-champ-select/v1/session",
            method="get")
        
        print(res.status_code, res.text)
        if not res.status_code == 200:
            return res
        actions = json.loads(res.text)
        """

        data = {
            "actorCellId": 0,
            "championId": champ_id, # Aphelios
            "completed": True,
            "id": 1,
            "isAllyAction": True,
        }
        res = self.request(
            suffix_url="/lol-champ-select/v1/session/actions/2",
            method="patch",
            data=data)
        return res