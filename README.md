## PukekoBot
A Slack bot that checks the status of servers and webpages

# run.py
Starts a flask app to run the bot within.
Manages all the event subscription messages from slack.

# bot.py
Holds all the functions to process the commands pukekobot recieves.
Commands:
hi pukeko - replies to you
pukeko status - Checks the statuses of online sites and posts the results

# Installation
wget https://bootstrap.pypa.io/pip/3.6/get-pip.py
python3 get-pip.py
python3 -m pip install slackclient slackeventsapi Flask
python3 run.py

Should close and create a config.txt file eventually to add tokens to manually