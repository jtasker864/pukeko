from urllib.request import urlopen
from urllib.error import *

class PukekoBot:
    
    def __init__(self, channel, text):
        self.channel = channel
        self.text = text

    def _test_status(self, site):
        # try block to read URL
        try:
            html = urlopen(site)
        except HTTPError as e:
            return ":red_circle: *HTTP ERROR*"
        except URLError as e:
            return ":red_circle: *URL ERROR*"
        else:
            return ":large_green_circle: Working fine"
    
    def _get_message_block(self, message):
        return {"type": "section", "text": {"type": "mrkdwn", "text": message}}

    def _list_statuses(self):
        site_list = ["https://www.google.com/", "https://urbanintelligence.co.nz/", "http://fakesitedoesntexist.com/"]
        statuses = ""
        for site in site_list:
            status = self._test_status(site)
            statuses += site + ': ' + status + "\n"
        return statuses

    def _get_status_payload(self):
        return {
            "channel": self.channel,
            "blocks": [
                self._get_message_block("Server statuses:"),
                self._get_message_block(self._list_statuses()),
            ],
        }

    def _get_hi_payload(self):
        return {
            "channel": self.channel,
            "blocks": [
                self._get_message_block("Hi <3"),
            ],
        }

    def get_message_payload(self):
        if self.text == "hi pukeko":
            return self._get_hi_payload()
        elif self.text == "pukeko status":
            return self._get_status_payload()