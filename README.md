# General Purpose Discord Bot

Welcome! This is my project for CS407. Instructions are listed below.

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

Once you've downloaded/cloned and opened up the files, locate the main.py file, in which you'll see that you need to insert a bot token in line 8.
To get the bot token, go back to the Discord Developer page, and under the Bot tab, click Reset Token and copy it, then assign that value as a string
for the TOKEN variable on line 8. You may also want to assign GUILD_ID in which you right-click on your server's picture and click "copy id."

```python
...
# Initialize bot
TOKEN = '<your token goes here>'
GUILD_ID = discord.Object(id= <your guild id goes here>)
...
```

Once that is all completed, run main.py, and the bot should be up and running!
