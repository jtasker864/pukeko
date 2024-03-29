from re import L
from tabnanny import check
from urllib.request import urlopen
from urllib.error import *
from xml.dom import SyntaxErr
from slack import WebClient
import json
from datetime import datetime, timedelta

class PukekoBot:
    
    #Starts the bot by creating a sites.json file if none is there
    def __init__(self, start_channel, token, sysargs, debug=False):
        self.sysargs = sysargs
        self.botname = "unnamed"
        self.nextpoll = None
        if len(self.sysargs) > 1:
            self.botname = " ".join(self.sysargs[1:])
        self.polling = False
        self.debug = debug
        self.status_payload = None
        self.status_response = None
        self.sleeptime = 60*5
        self.are_sites_down = False
        self._check_sites_file()
        self.web_client = None
        if not debug:
            self.web_client = WebClient(token=token)
        self.start_channel = start_channel
        if debug:
            self._post("ayo")
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
                        "description": "Our main wordpress page"
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
    
    def _edit_payload(self, payload, response, messages):
        payload["blocks"] = [self._get_message_block(message) for message in messages]
        if self.debug:
            return payload
        payload["ts"] = response.get("ts")
        payload["channel"] = response.get("channel")
        return payload
    
    def _send_payload(self, payload):
        #print(payload)
        if self.debug:
            for paragraph in (block.get("text").get("text") for block in payload.get("blocks")):
                print(paragraph)
            return
        response = self.web_client.chat_postMessage(**payload)
        return response

    def _send_payload_edit(self, payload):
        if self.debug:
            for paragraph in (block.get("text").get("text") for block in payload.get("blocks")):
                print("EDIT: " + paragraph)
            return
        self.web_client.chat_update(**payload)

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
            status = self._test_site_status(site.get("site"))
            if status not in [200, 401]:
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
            message = "*URL ERROR* :" + site.get("site") + " - " + site.get("description")
        else:
            message = "*HTTP ERROR " + str(status) + "*: " + site.get("site") + " - " + site.get("description")
        return message

    def _list_statuses(self, channel):
        statuses = ""
        for site in self.sites:
            status = self._test_site_status(site.get("site"))
            statuses += self._status_string(site, status) + "\n"
        self._post("Server Statuses:", statuses, channel=channel)

    def _say_hi(self, channel):
        self._post("Hi from " + self.botname + " <3", channel=channel)

    def _get_statuses(self, nextpolltime=0):
        resend = False
        now = datetime.now()
        broken_sites = []
        for site in self.sites:
            status = self._test_site_status(site.get("site"))
            if status not in [200, 401]:
                broken_sites.append((site, status))
        messages = []
        if len(broken_sites) == 0:
            messages.append(":large_green_circle: All sites seem healthy. All is good! :large_green_circle:")
            if self.are_sites_down == True:
                self.are_sites_down = False
                self._post("All sites are healthy again :)")
                resend = True
        else:
            messages.append(f":red_circle: {len(broken_sites)} site(s) were found to be down :red_circle:")
            statuses = ""
            for i, (site, status) in enumerate(broken_sites):
                statuses += str(i+1) + ") " + self._status_string(site, status) + "\n"
            messages.append(statuses)
            if self.are_sites_down == False:
                self.are_sites_down = True
                self._post("<!channel> it seems a site has gone down :(")
                resend = True
        messages.append("Checked by " + self.botname + "\n" +\
            now.strftime("Checked on %d/%m/%y at %I:%M:%S %p"))
        if nextpolltime != 0:
            self.nextpoll = now + timedelta(seconds=nextpolltime)
        if self.nextpoll != None:
            messages[-1] += self.nextpoll.strftime("\n" + "Next poll due at %I:%M:%S %p")
        return messages, resend

    def _update_status(self, channel, polltime=0):
        statuses, resend = self._get_statuses(nextpolltime=polltime)
        if self.status_payload == None or resend:
            self.status_payload = self._get_payload(channel, statuses)
            self.status_response = self._send_payload(self.status_payload)
        else:
            self.status_payload = self._edit_payload(self.status_payload, self.status_response, statuses)
            self._send_payload_edit(self.status_payload)

    def _make_site_json(self, site, description, check_regularly):
        return \
            {
                "site": site,
                "description": description
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
            sites_str += str(i+1) + ": " + site.get("site") + " - " + site.get("description")
            sites_str += "\n"
        self._post("Sites:", sites_str, channel=channel)

    #Public functions

    def process_message(self, channel, text):
        if text == "hi pukeko":
            self._say_hi(channel)
        elif text == "pukeko status":
            self._update_status(channel)
        elif text == "pukeko reload":
            self._check_sites_file()
            self._post("Reloaded sites.json")
        # elif text.startswith("pukeko add "):
        #     self._add_site(channel, text)
        # elif text.startswith("pukeko remove "):
        #     self._remove_site(channel, text)
        elif text == "pukeko list":
            self._list_sites(channel)
        # elif text == "pukeko poll":
        #     self.start_polling()
        elif text == "exit":
            self.debug_running = False

if __name__ == "__main__": #Means we're debugging
    pukeko = PukekoBot("#start", "authc00de", ["run.py", "test bot"], debug=True)
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
