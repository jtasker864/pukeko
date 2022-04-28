from re import L
from tabnanny import check
from urllib.request import urlopen
from urllib.error import *
from xml.dom import SyntaxErr
from slack import WebClient
import json

class PukekoBot:
    
    def __init__(self, start_channel, token, connect=True):
        self._check_sites_file()
        self.connect = connect
        if connect:
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
        print("CREATING JSON SITES FILE")
        self.sites = [{
                        "site": "https://urbanintelligence.co.nz/",
                        "description": "Our main wordpress page",
                        "test-regularly": True
                    }]
        self._write_sites()
    
    def _update_sites(self, file):
        data = json.load(file)
        self.sites = data.get("sites")

    def _write_sites(self):
        print("SAVING JSON SITES FILE")
        content = \
            {
                "sites": self.sites
            }
        with open('sites.json', 'w') as outfile:
            json.dump(content, outfile, indent=4)

    #Basic messaging functionality
    
    def _get_message_block(self, message):
        return {"type": "section", "text": {"type": "mrkdwn", "text": message}}

    def _get_payload(self, channel, messages):
        return {
            "channel": channel,
            "blocks": [self._get_message_block(message) for message in messages],
        }
    
    def _send_payload(self, payload):
        if self.connect:
            self.web_client.chat_postMessage(**payload)
        else:
            print(payload)

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
            statuses += site.get("site") + ': ' + status + "\n"
        payload = self._get_payload(channel, ["Server Statuses:", statuses])
        self._send_payload(payload)

    def _say_hi(self, channel):
        payload = self._get_payload(channel, ["Hi <3"])
        self._send_payload(payload)

    def _make_site_json(self, site, description, check_regularly):
        return \
            {
                "site": site,
                "description": description,
                "test-regularly": check_regularly
            }

    def _read_add_site_string(self, text):
        pointer = 11 #crops out "pukeko add "
        if text[pointer] != '\"':
            raise SyntaxError
        pointer += 1
        after_last_quote = pointer
        while text[pointer] != "\"":
            pointer += 1
        site = text[after_last_quote:pointer]
        if text[pointer:pointer + 3] != '\" \"':
            raise SyntaxError
        pointer += 3
        after_last_quote = pointer
        while text[pointer] != "\"":
            pointer += 1
        description = text[after_last_quote:pointer]
        pointer += 2
        check_regularly_str = text[pointer:].lower()
        print(check_regularly_str)
        if check_regularly_str != "true" and check_regularly_str != "false":
            raise SyntaxError
        check_regularly = bool(text[pointer:])
        return site, description, check_regularly


    def _add_site(self, channel, text):
        try:
            site, description, check_regularly = self._read_add_site_string(text)
            new_site = self._make_site_json(site, description, check_regularly)
            self.sites.append(new_site)
            self._write_sites()
            payload = self._get_payload(channel, ["Added " + site])
            self._send_payload(payload)
        except SyntaxError: 
            payload = self._get_payload(channel, ["that's some invalid syntax my dude"])
            self._send_payload(payload)

    #Public functions

    def process_message(self, channel, text):
        if text == "hi pukeko":
            self._say_hi(channel)
        elif text == "pukeko status":
            self._list_statuses(channel)
        elif text.startswith("pukeko add "):
            self._add_site(channel, text)

if __name__ == "__main__":
    pukeko = PukekoBot("#start", "authc00de", connect=False)
    pukeko.process_message("#test", "nothing")
    pukeko.process_message("#test", "pukeko")
    pukeko.process_message("#test", "hi pukeko")
    pukeko.process_message("#test", "pukeko status")
    #pukeko.process_message("#test", "pukeko add \"google.com\" \"description here\" true")