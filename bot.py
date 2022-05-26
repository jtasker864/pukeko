from re import L
from tabnanny import check
from urllib.request import urlopen
from urllib.error import *
from xml.dom import SyntaxErr
from slack import WebClient
import json
from datetime import datetime
import time
from multiprocessing import Process

class PukekoBot:
    
    #Starts the bot by creating a sites.json file if none is there and posting "ayo"
    def __init__(self, start_channel, token, debug=False):
        self.polling = False
        self.debug = debug
        self._check_sites_file()
        self.web_client = None
        if not debug:
            self.web_client = WebClient(token=token)
        self.start_channel = start_channel
        self._post("ayo")
        if debug:
            self._start_debug()
    
    def _start_debug(self):
        self.debug_running = True
        while self.debug_running:
            message = input()
            self.process_message("Debug", message)
        self._post("Debug exited")

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
                        "test-regularly": True,
                        "poll-status": "Working"
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
        if self.debug:
            for paragraph in paragraphs:
                print(paragraph)
            return
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
        self.web_client.chat_postMessage(**payload)

    #Specific command functionality

    #Returns none OR the site http code
    def _test_site_status(self, site):
        # try block to read URL
        try:
            html = urlopen(site)
        except HTTPError as e:
            return e.code
        except URLError as e:
            return None
        return html.getcode()

    #Prints a message to the starting channel if a site is disabled
    def run_status_poll(self):
        now = datetime.now()
        now_str = now.strftime("%d/%m/%Y %H:%M:%S")
        broken_sites = []
        for site in self.sites:
            if not site.get("test-regularly"):
                continue
            status = self._test_site_status(site.get("site"))
            if status != 200:
                broken_sites.append((site, status))
        if len(broken_sites) > 0:
            statuses = ""
            for site, status in broken_sites:
                statuses += self._status_string(site, status) + "\n"
            self._post("A poll at " + now_str + " found these sites down:", statuses)
            return False
        else:
            return True

    def _status_string(self, site, status):
        message = None
        if status == 200:
            message = site.get("site") + ": :large_green_circle: Working fine"
        elif status == None:
            message = site.get("site") + ": :red_circle: *URL ERROR*"
        else:
            message = site.get("site") + ": :red_circle: *HTTP ERROR " + str(status) + "*"
        return message

    def _list_statuses(self, channel):
        statuses = ""
        for site in self.sites:
            status = self._test_site_status(site.get("site"))
            statuses += self._status_string(site, status) + "\n"
        self._post("Server Statuses:", statuses, channel=channel)

    def _say_hi(self, channel):
        self._post("Hi <3", channel=channel)

    def _make_site_json(self, site, description, check_regularly):
        return \
            {
                "site": site,
                "description": description,
                "test-regularly": check_regularly,
                "poll-status": "Working"
            }

    #Reads a sting of form "pukeko add "SITE" "DESCRIPTION" CHECKREGULARLY"
    #i.e. pukeko add "google.com" "google's site is probably going to be up all the time" true
    def _read_add_site_string(self, text):
        pointer = 0

        #Check for 'pukeko add "'
        add_str = 'pukeko add \"'
        if text[pointer:pointer + len(add_str)] != add_str:
            raise SyntaxError
        pointer += len(add_str)

        #Seeks next " apostrophe
        after_last_quote = pointer
        while text[pointer] != "\"":
            pointer += 1

        #Takes SITE contents between apostrophes
        site = text[after_last_quote:pointer]

        #Check for '" "'
        apostrophes = '\" \"'
        if text[pointer:pointer + len(apostrophes)] != apostrophes:
            raise SyntaxError
        pointer += len(apostrophes)

        #Seeks next " apostrophe
        after_last_quote = pointer
        while text[pointer] != "\"":
            pointer += 1
        
        #Takes DESCRIPTION contents between apostrophes
        description = text[after_last_quote:pointer]

         #Check for '" '
        apostrophe = '\" '
        if text[pointer:pointer + len(apostrophe)] != apostrophe:
            raise SyntaxError
        pointer += len(apostrophe)

        #Converts rest of string to a boolean
        check_regularly = (text[pointer:].lower() == "true")
        if (not check_regularly) and (text[pointer:].lower() != "false"):
            raise SyntaxError
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

    def _read_remove_site_string(self, text):
        pointer = 0

        #Check for 'pukeko remove '
        remove_str = 'pukeko remove '
        if text[pointer:pointer + len(remove_str)] != remove_str:
            raise SyntaxError
        pointer += len(remove_str)

        try:
            index = int(text[pointer:]) - 1
        except ValueError:
            raise SyntaxError
        return index
        
    def _remove_site(self, channel, text):
        try:
            index = self._read_remove_site_string(text)
            if index >= len(self.sites) or index < 0:
                self._post("that's out of the range innit", channel=channel)
                return
            removed_site = self.sites.pop(index)
            self._write_sites()
            self._post("removed " + removed_site.get("site"), channel=channel)
        except SyntaxError: 
            self._post("that's some invalid syntax my dude", channel=channel)

    def _list_sites(self, channel):
        sites_str = ""
        for i, site in enumerate(self.sites):
            sites_str += str(i+1) + ": " + site.get("site") + " - " + site.get("description") + " - "
            if site.get("test-regularly"):
                sites_str += "Checking regularly"
            else:
                sites_str += "Not checking"
            sites_str += "\n"
        self._post("Sites:", sites_str, channel=channel)

    def _poll_regularly(self):
        self.polling = self.run_status_poll()
        while self.polling:
            time.sleep(10)
            self.polling = self.run_status_poll()
        self._post("Stopping polling")

    #Public functions

    def start_polling(self):
        self._post("Starting polling")
        self.polling = True
        poller = Process(target = self._poll_regularly)
        poller.start()

    def process_message(self, channel, text):
        if text == "hi pukeko":
            self._say_hi(channel)
        elif text == "pukeko status":
            self._list_statuses(channel)
        elif text.startswith("pukeko add "):
            self._add_site(channel, text)
        elif text.startswith("pukeko remove "):
            self._remove_site(channel, text)
        elif text == "pukeko list":
            self._list_sites(channel)
        elif text == "pukeko poll":
            self.start_polling()
        elif text == "exit":
            self.debug_running = False

if __name__ == "__main__": #Means we're debugging
    pukeko = PukekoBot("#start", "authc00de", debug=True)
    # pukeko.process_message("#test", "nothing")
    # pukeko.process_message("#test", "pukeko")
    # pukeko.process_message("#test", "hi pukeko")
    # pukeko.process_message("#test", "pukeko status")
    # pukeko.process_message("#test", "pukeko list")
    # pukeko.process_message("#test", "pukeko poll")
    # # pukeko.start_polling("#test")
    # time.sleep(600)
    # pukeko.process_message("#test", "pukeko remove -12")
    # pukeko.process_message("#test", "pukeko remove x")
    # pukeko.run_status_poll()
    # pukeko.process_message("#test", "pukeko status")
    # pukeko.process_message("#test", "pukeko add \"google.com\" \"description here\" true")
    # pukeko.process_message("#test", "pukeko add \"false.com\" \"false here\" false")
    # pukeko.process_message("#test", "pukeko add \"falsey.com\" \"broken\" falsey")
    # pukeko.process_message("#test", "pukeko add djsafholk23\"D\"A")
