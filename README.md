# PukekoBot
A Slack bot that checks the status of servers and webpages

# Installation
## Downloading the bot
Enter the following commands into the terminal (written for Ubuntu).
```
git clone https://github.com/jtasker864/pukeko.git
wget https://bootstrap.pypa.io/pip/3.6/get-pip.py
python3 get-pip.py
python3 -m pip install slackclient slackeventsapi Flask
cd pukeko
[create config.txt formatted as shown below]
python3 run.py
```
Make sure you create a config.txt file before running.

## Configure the bot
- Go to https://api.slack.com and make a new bot, setup name and image.
- Subscribe to the bot event "message.channels" and "channels:history" and "channels:write" scopes.
- Install to workplace, taking the OAuth code and putting it in config.txt.
- Specify the desired status channel as starting-channel in config.txt.
- IMPORTANT: ADD THE BOT TO THE STARTING CHANNEL IN THE SLACK CLIENT OR IT WON'T POST OR READ ANYTHING
- Add the signing secret shown in the main bot page of https://api.slack.com.
- Set event descriptions to redirect to http://IP:3000/slack/events, with IP being the IP of the server this bot is installed on.
- NOTE: The bot must be running for slack to verify the IP.

## config.txt
The config should be formatted as follows:
```
starting-channel: #example-channel
oauth-token: [insert here]
signing-secret: [insert here]
```

## sites.json
The basic format will be generated when the bot is first run. It should be easy to configure this if you know .json's format.

# Code Documantation
## run.py
Starts a flask app to run the bot within.
Manages all the event subscription messages from slack using Flask as the mini web server with slackeventsapi to process messages.

## bot.py
Holds all the functions to process the commands pukekobot recieves.
Commands:
hi pukeko - replies to you
pukeko status - Checks the statuses of online sites and posts the results
pukeko add "SITE" "DESCRIPTION" CHECKREGULARLY
pukeko list - lists sites

# poll-status
This tag contains the 'polling state' of the site
"Working": The site is operational and not returning a URL or HTTP error
"Error 0": The site just had an error, and notifies the chat once
"Error 5": The site is polled again in 15 minutes
"Error 10": 10 min poll
"Down": 15 minute poll was done with no results found - polling is then paused and another notification is sent

Any non-error polls return the status to "Working"

# Extended Site List as of September
```
{
    "sites": [
        {
            "site": "https://urbanintelligence.co.nz/",
            "description": "Our main wordpress page"
        },
        {
            "site": "https://urbanintelligence.co.nz/expertise/",
            "description": "Our expertise page"
        },
        {
            "site": "https://urbanintelligence.co.nz/news/",
            "description": "Our news & research page"
        },
        {
            "site": "https://urbanintelligence.co.nz/about/",
            "description": "Our about us page"
        },
        {
            "site": "https://urbanintelligence.co.nz/privacy-policy/",
            "description": "Our privacy policy page"
        },
        {
            "site": "https://projects.urbanintelligence.co.nz/chap",
            "description": "CHAP"
        },
        {
            "site": "https://projects.urbanintelligence.co.nz/mrapple",
            "description": "Mr Apple"
        },
        {
            "site": "https://projects.urbanintelligence.co.nz/mrapple-jonz/",
            "description": "JoNZ"
        },
        {
            "site": "https://projects.urbanintelligence.co.nz/wremo/",
            "description": "WREMO"
        },
        {
            "site": "https://projects.urbanintelligence.co.nz/scales/",
            "description": "Scales Corp."
        },
        {
            "site": "https://projects.urbanintelligence.co.nz/risk-intelligence-demo/",
            "description": "Risk Intelligence Demo"
        },
        {
            "site": "https://projects.urbanintelligence.co.nz/access-resilience/",
            "description": "Access Resilience"
        },
        {
            "site": "https://projects.urbanintelligence.co.nz/chap-public/",
            "description": "CHAP public (unsure what this is for)"
        },
        {
            "site": "https://projects.urbanintelligence.co.nz/nz-coastal-risk/",
            "description": "NZ Coastal Risk"
        },
        {
            "site": "https://projects.urbanintelligence.co.nz/slr-usa/",
            "description": "Sea Level Rise - USA"
        },
        {
            "site": "https://projects.urbanintelligence.co.nz/x-minute-city/",
            "description": "The 10 Minute City"
        }
    ]
}
```