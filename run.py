import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from bot import PukekoBot

# Initialize a Flask app to host the events adapter
app = Flask(__name__)

# Create an events adapter and register it to an endpoint in the slack app for event ingestion.
slack_events_adapter = SlackEventAdapter("89f2088835b23f7f0083ad2009e61c81", "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token="xoxb-522742488742-3430285821799-aaDOCg3oX8J0DEZpmrIWcwBA")

def start_pukeko(channel, text):
    # Get a new CoinBot
    pukeko = PukekoBot(channel, text)

    # Get the onboarding message payload
    message = pukeko.get_message_payload()

    # Post the onboarding message in Slack
    if(message is not None):
        slack_web_client.chat_postMessage(**message)

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

    # Check and see if the activation phrase was in the text of the message.
    # If so, execute the code to flip a coin.
    if "pukeko" in text.lower():
        # Since the activation phrase was met, get the channel ID that the event
        # was executed on
        channel_id = event.get("channel")

        # Execute the flip_coin function and send the results of
        # flipping a coin to the channel
        return start_pukeko(channel_id, text)

if __name__ == "__main__":
    # Create the logging object
    logger = logging.getLogger()

    # Set the log level to DEBUG. This will increase verbosity of logging messages
    logger.setLevel(logging.DEBUG)

    # Add the StreamHandler as a logging handler
    logger.addHandler(logging.StreamHandler())

    # Run your app on your externally facing IP address on port 3000 instead of
    # running it on localhost, which is traditional for development.
    app.run(host='0.0.0.0', port=3000)