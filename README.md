<div align="center">
    <a href="https://www.youtube.com/watch?v=xtlteIFVrR8"
       target="_blank">
       <img src="http://img.youtube.com/vi/xtlteIFVrR8/0.jpg"
            alt="League of Legends (TLoL-RL): Reinforcement Learning (Part 1 - Setup)"
            width="240" height="180" border="10" />
    </a>
</div>

# TLoL-RL - League of Legends Reinforcement Learning Library

TLoL-RL (Reinforcement Learning Python Module) - League of Legends RL Module (Allows ML Models to Play League of Legends). It provides an interface for an agent to play
League of Legends using an OpenAI Gym interface, similar to [pylol](https://github.com/MiscellaneousStuff/pylol) which is originally based of [pysc2](https://github.com/deepmind/pysc2) for Starcraft 2.

## About

Disclaimer: This project is not affiliated with Riot Games in any way.

If you are interested in using this project or are just curious, send an email to
[raokosan@gmail.com](mailto:raokosan@gmail.com).

# Quick Start Guide

## Locally

To run an agent locally, you will first need to log into League of Legends.
It is recommended to use a separate account from your main account when using
the `tlol-rl` module as your main account may be detected as a bot.

## Get TLoL-RL

### From Source

You can install TLoL-RL from a local clone of the git repo:

```bash
git clone https://github.com/MiscellaneousStuff/tlol-rl.git
pip install -e tlol-rl/
```

## Config

Once you have TLoL-RL installed, you will need to create a `config.txt` file.
This needs to be located in the same working directory as any call to
`python -m tlol_rl.bin.agent` or any other `tlol_rl.bin` script which relies
on `config.txt`. The configuration file uses the following format:

```bash
[dirs]
tlol_rl_server = ..\Path\To\LView\
lol_client     = ..\Path\To\Riot Games\League of Legends\
```

## Running

To test run the environment, go to where your config.txt file is and 
run:

```bash
python -m tlol_rl.bin.agent --champion "Ezreal"
```

You can replace "Ezreal" with any champion that your account owns!
Between runs, you need to make sure that `ConsoleApplication.exe`
has been stopped. Go to Task Manager and end the process if it
is still running. You also need to make sure that `dump.rdb` is
deleted if it exists in the same folder as `config.txt`. These
issues will be fixed in the future.