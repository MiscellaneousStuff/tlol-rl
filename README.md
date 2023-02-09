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
git clone git clone https://github.com/MiscellaneousStuff/tlol-rl.git
pip install --upgrade tlol-rl/
```

## Config

Once you have TLoL-RL installed, you will need to create a `config.txt` with
the following format:

```bash
[dirs]
tlol_rl_server = .../Server.exe
```