from urllib.request import urlopen
from urllib.error import *
from slack import WebClient

class PukekoBot:
    
    def __init__(self, token):
        self.web_client = WebClient(token=token)

    #Basic messaging functionality
    
    def _get_message_block(self, message):
        return {"type": "section", "text": {"type": "mrkdwn", "text": message}}

    def _get_payload(self, channel, messages):
        return {
            "channel": channel,
            "blocks": [self._get_message_block(message) for message in messages],
        }
    
    def _send_payload(self, payload):
        print("Sending:")
        print(payload)
        self.web_client.chat_postMessage(**payload)

    #Specific command functionality

    def _test_site_status(self, site):
        # try block to read URL
        try:
            html = urlopen(site)
        except HTTPError as e:
            return ":red_circle: *HTTP ERROR*"
        except URLError as e:
            return ":red_circle: *URL ERROR*"
        else:
            return ":large_green_circle: Working fine"

    def _list_statuses(self, channel):
        site_list = ["https://www.google.com/", "https://urbanintelligence.co.nz/", "http://fakesitedoesntexist.com/"]
        statuses = ""
        for site in site_list:
            status = self._test_status(site)
            statuses += site + ': ' + status + "\n"
        payload = self._get_payload(channel, ["Server Statuses:", statuses])
        self._send_payload(payload)

    def _say_hi(self, channel):
        payload = self._get_payload(channel, ["Hi <3"])
        self._send_payload(payload)

    #Public functions

    def process_message(self, channel, text):
        if text == "hi pukeko":
            return self._say_hi(channel)
        elif text == "pukeko status":
            return self._list_statuses(channel)
        