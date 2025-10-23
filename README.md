# General Purpose Discord Bot

Welcome! This is a simple multi-purpose Discord chatbot. Instructions are listed below.

## Installation

First, install the discord module on your system if you don't have it (most importantly, make sure you have [Python](https://www.python.org/downloads/) installed). Installing in a virtual environment is recommended.

```bash
# Linux/macOS
python3 -m pip install -U discord.py

# Windows
py -3 -m pip install -U discord.py
```

## Set Up Bot on Discord Developer site

Go to the Applications tab on the [discord developer site](https://discord.com/developers/docs/intro) where you will be prompted to log in.
From here, go through the following steps to set up your bot:

- On the top right corner, click New Application; give the application a name and create
- Next, go to the Bot tab, where you can assign your bot a name, avatar, and banner
    - Staying in the Bot tab, scroll down, then turn on Public Bot and Message Content Intent
- Now go to the Installation tab and check Guild Install, select Discord Provided Link, and under Default Install Settings, select bot as a scope and permissions of your choice
    - Copy and paste the install link in another tab to add the bot to your server of choice

## Downloading/Cloning Repo

Please keep the Discord Developer tab up as you will need to go back to it later. You can now download the repo, or clone it using SSH:

```bash
git clone git@github.com:anvovn/cs407-project.git
```

## Assigning Bot Token

Once you've downloaded/cloned and opened up the files, make a new file named ".env" in the same directory as "main.py" and enter the following in it:

```python
# In ".env"
DISCORD_TOKEN = <your token goes here>
```
You'll want to make sure that you have dotenv installed:

```bash
pip install python-dotenv
```

When that is all completed, run "main.py," and the bot should be up and running!
