import logging
from flask import Flask
# from slack import WebClient
from slackeventsapi import SlackEventAdapter
from bot import PukekoBot
from multiprocessing import Process
import time
import sys

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

pukeko = PukekoBot(start_channel, oauth, sys.argv)

# When a 'message' event is detected by the events adapter, forward that payload
# to this function.
@slack_events_adapter.on("message")
def message(payload):
    # Get the event data from the payload
    event = payload.get("event", {})

    # Get the text from the event that came through
    text = event.get("text")
    
    channel_id = event.get("channel")

    if text is not None and "pukeko" in text.lower():
        return pukeko.process_message(channel_id, text)

def start_polling():
    pukeko.polling = True
    poller = Process(target = poll_regularly, args=(pukeko,))
    poller.start()

def poll_regularly(bot):
    while bot.polling:
        bot._update_status(start_channel, polltime=bot.sleeptime)
        time.sleep(bot.sleeptime)

if __name__ == "__main__":
    pukeko._post("ayo")
    start_polling()
    
    # Run your app on your externally facing IP address on port 3000 instead of
    # running it on localhost, which is traditional for development.
    app.run(host='0.0.0.0', port=3000)
    print("Closed Flask")

    # import time
    # payload = pukeko._get_payload("#site-status", ["editing me"])
    # response = pukeko._send_payload(payload)
    # print(payload)
    # print()
    # print()
    # print(response)
    # print()
    # print()
    # time.sleep(10)
    # payload = pukeko._edit_payload(payload, response, ["edited"])
    # print(payload)
    # pukeko._send_payload_edit(payload)

    # Create the logging object
    # logger = logging.getLogger()

    # # Set the log level to DEBUG. This will increase verbosity of logging messages
    # logger.setLevel(logging.DEBUG)

    # # Add the StreamHandler as a logging handler
    # logger.addHandler(logging.StreamHandler())
