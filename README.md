# General Purpose Discord Bot

**Welcome! This is my project for CS407. Instructions listed below.**

## Installation

Please make sure you have the discord module downloaded on your system

```bash
# Linux/macOS
python3 -m pip install -U discord.py

# Windows
py -3 -m pip install -U discord.py
```

## Set Up Bot on Discord Developer site

Go to the Applications tab on the [discord developer site](https://discord.com/developers/docs/intro) where you will be prompted to log in.
From here, go through the following steps to set up your bot:

- On the top right corner, click New Application; give it the application a name and create.
- Next, go to the Bot tab, where you can assign your bot a name, avatar and banner
    - Staying in the Bot tab, sscroll down, then turn on Public Bot and Message Content Intent
- Now go to the Installation tab and check Guild Intall, select Discord Provided Link, and under Default Install Settings, select bot as a scope and permissions of your choice
    - Copy and paste the install link in another tab to add the bot to your server of choice

## Downloading/Cloning Repo

Please keep the Discord Developer tab up as you will need to go back to it later. You can now download the repo, or clone it using SSH:

```bash
git clone git@github.com:anvovn/cs407-project.git
```

## Assigning Bot Token

Once you've downloaded/cloned and opened up the files, locate the main.py file, in which you'll see that you need to insert a bot token in line 8.
To get the bot token, go back to the Discord Developer page, and under the Bot tab, click Reset Token and copy it, then assign that value as a string
for the TOKEN variable on line 8.

```python
...
# Initialize bot
TOKEN = '<your token goes here>'
...
```

Once that is all completed. Run main.py and your bot should be up and running!