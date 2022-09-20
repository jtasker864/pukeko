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
pukeko add "SITE" "DESCRIPTION" CHECKREGULARLY
pukeko list - lists sites

# Installation
wget https://bootstrap.pypa.io/pip/3.6/get-pip.py
python3 get-pip.py
python3 -m pip install slackclient slackeventsapi Flask
python3 run.py

Should close and create a config.txt file eventually to add tokens to manually

Add the parameters and ADD TO THE CHANNEL MENTIONED

# sites.json

# poll-status
This tag contains the 'polling state' of the site
"Working": The site is operational and not returning a URL or HTTP error
"Error 0": The site just had an error, and notifies the chat once
"Error 5": The site is polled again in 15 minutes
"Error 10": 10 min poll
"Down": 15 minute poll was done with no results found - polling is then paused and another notification is sent

Any non-error polls return the status to "Working"


test