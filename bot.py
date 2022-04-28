from re import L
from urllib.request import urlopen
from urllib.error import *
from slack import WebClient
import json

class PukekoBot:
    
    def __init__(self, start_channel, token):
        self._check_sites_file()
        for site in self.sites:
            print(site)
        self.web_client = WebClient(token=token)
        payload = self._get_payload(start_channel, ["ayo"])
        self._send_payload(payload)

    #JSON reading / writing
    def _check_sites_file(self):
        f = None
        try:
            f = open("sites.json")
        except FileNotFoundError:
            self._create_sites_file()
            f = open("sites.json")
        self._update_sites(f)

    def _create_sites_file(self):
        content = \
            {
                "sites": [
                    {
                        "site": "https://urbanintelligence.co.nz/",
                        "description": "Our main wordpress page",
                        "test-regularly": True
                    }
                ]
            }
        with open('sites.json', 'w') as outfile:
            json.dump(content, outfile, indent=4)
    
    def _update_sites(self, file):
        data = json.load(file)
        self.sites = data.get("sites")

    #Basic messaging functionality
    
    def _get_message_block(self, message):
        return {"type": "section", "text": {"type": "mrkdwn", "text": message}}

    def _get_payload(self, channel, messages):
        return {
            "channel": channel,
            "blocks": [self._get_message_block(message) for message in messages],
        }
    
    def _send_payload(self, payload):
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
        statuses = ""
        for site in self.sites:
            status = self._test_site_status(site.get("site"))
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

pukeko = PukekoBot("", "")