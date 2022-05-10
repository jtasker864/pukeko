from re import L
from tabnanny import check
from urllib.request import urlopen
from urllib.error import *
from xml.dom import SyntaxErr
from slack import WebClient
import json

class PukekoBot:
    
    #Starts the bot by creating a sites.json file if none is there and posting "ayo"
    def __init__(self, start_channel, token, is_connecting=True):
        self._check_sites_file()
        if is_connecting:
            self.web_client = WebClient(token=token)
        else:
            self.web_client = None
        self.start_channel = start_channel
        self._post("ayo")

    #JSON reading / writing
    def _check_sites_file(self):
        f = None
        try:
            f = open("sites.json")
        except FileNotFoundError:
            self._create_sites_file()
            f = open("sites.json")
        data = json.load(f)
        self.sites = data.get("sites")

    def _create_sites_file(self):
        print("CREATING JSON SITES FILE")
        self.sites = [{
                        "site": "https://urbanintelligence.co.nz/",
                        "description": "Our main wordpress page",
                        "test-regularly": True
                    }]
        self._write_sites()

    def _write_sites(self):
        print("SAVING JSON SITES FILE")
        content = \
            {
                "sites": self.sites
            }
        with open('sites.json', 'w') as outfile:
            json.dump(content, outfile, indent=4)

    #Basic messaging functionality

    #Posts the lines given to the channel
    #Each line is treated as a paragraph, for small line breaks use \n in the string
    def _post(self, *paragraphs, channel=None):
        if channel == None:
            channel = self.start_channel
        payload = self._get_payload(channel, paragraphs)
        self._send_payload(payload)
        
    
    def _get_message_block(self, message):
        return {"type": "section", "text": {"type": "mrkdwn", "text": message}}

    def _get_payload(self, channel, messages):
        return {
            "channel": channel,
            "is_app_unfurl": False,
            "blocks": [self._get_message_block(message) for message in messages],
        }
    
    def _send_payload(self, payload):
        if self.web_client != None:
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
        self._post("Server Statuses:", statuses, channel=channel)

    def _say_hi(self, channel):
        self._post("Hi <3", channel=channel)

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
            self._post("Added " + site, channel=channel)
        except SyntaxError: 
            self._post("that's some invalid syntax my dude", channel=channel)
        
    def _list_sites(self, channel):
        sites_str = ""
        for site in self.sites:
            sites_str += site.get("site") + " - " + site.get("description") + " - "
            if site.get("test-regularly"):
                sites_str += "Checking regularly"
            else:
                sites_str += "Not checking"
            sites_str += "\n"
        self._post("Sites:", sites_str, channel=channel)

    #Public functions

    def process_message(self, channel, text):
        if text == "hi pukeko":
            self._say_hi(channel)
        elif text == "pukeko status":
            self._list_statuses(channel)
        elif text.startswith("pukeko add "):
            self._add_site(channel, text)
        elif text == "pukeko list":
            self._list_sites(channel)

if __name__ == "__main__":
    pukeko = PukekoBot("#start", "authc00de", is_connecting=False)
    pukeko.process_message("#test", "nothing")
    pukeko.process_message("#test", "pukeko")
    pukeko.process_message("#test", "hi pukeko")
    #pukeko.process_message("#test", "pukeko status")
    pukeko.process_message("#test", "pukeko add \"google.com\" \"description here\" true")
    pukeko.process_message("#test", "pukeko list")