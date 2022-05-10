import logging
from flask import Flask
# from slack import WebClient
from slackeventsapi import SlackEventAdapter
from bot import PukekoBot
import time
from multiprocessing import Process

def read_config():
    config_file = open("config.txt")
    lines = config_file.read().splitlines()
    line_parts = [line.split() for line in lines]
    start_channel = line_parts[0][1]
    oauth = line_parts[1][1]
    signing = line_parts[2][1]
    return start_channel, oauth, signing

start_channel, oauth, signing = read_config()

# Initialize a Flask app to host the events adapter
app = Flask(__name__)

# Create an events adapter and register it to an endpoint in the slack app for event ingestion.
slack_events_adapter = SlackEventAdapter(signing, server=app)

pukeko = PukekoBot(start_channel, oauth, is_connecting=False)

# When a 'message' event is detected by the events adapter, forward that payload
# to this function.
@slack_events_adapter.on("message")
def message(payload):
    """Parse the message event, and if the activation string is in the text,
    simulate a coin flip and send the result.
    """
    # Get the event data from the payload
    event = payload.get("event", {})

    # Get the text from the event that came through
    text = event.get("text")
    
    channel_id = event.get("channel")

    if text is not None and "pukeko" in text.lower():
        return pukeko.process_message(channel_id, text)

def poll_sites():
    print("Polling")
    


def poll_regularly():
    print("Starting polling")
    while True:
        time.sleep(3)
        poll_sites()

if __name__ == "__main__":
    poller = Process(target = poll_regularly)
    poller.start()

    # Create the logging object
    logger = logging.getLogger()

    # Set the log level to DEBUG. This will increase verbosity of logging messages
    logger.setLevel(logging.DEBUG)

    # Add the StreamHandler as a logging handler
    logger.addHandler(logging.StreamHandler())

    # Run your app on your externally facing IP address on port 3000 instead of
    # running it on localhost, which is traditional for development.
    app.run(host='0.0.0.0', port=3000)
    print("Closed Flask")
