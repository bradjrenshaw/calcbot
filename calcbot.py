from collections import deque
import os, sys

import command
import commands
import logging
sys.path.append(os.path.abspath("mbf"))

import mbf
from mbf.mudinfo import alter_aeon
import utils

logging.basicConfig(level=logging.ERROR)
info = {'name': 'calc', 'version': 0.1}

m = mbf.Mbf("alteraeon.com", alter_aeon, port=3010, username="calc", password="mathstuff", autoconnect=False, auto_login=False)

parser = command.parser(m, commands=commands.commands, info=info)

def send_channel(channel_name, msg):
	"""Send a given message to a given channel."""
	if msg != "":
		c = utils.channel_message(channel_name, msg)
		m.g['send_queue'].append(c)

def tell(who, msg):
	"""Given a person to send it to and a message, make a tell object and add it to our send queue."""
	t = utils.tell(who, msg)
	m.g['send_queue'].append(t)


def send(cmd):
	m.g['send_queue'].append(cmd)


@m.trigger(r"""^chn:(\(|\[)(?P<channel_name>[A-Za-z]+)(\)|\])\s+(?P<who>[A-Za-z]+):\s*(?P<msg>.+)\s*$""")
@m.trigger(r"""^chn:(?P<who>[A-Za-z]+)\s+(?P<channel_name>[A-Za-z]+)s(\,|\:)\s+('|)(?P<msg>.+?)\s*('|)\s*$""")
def handle_channel(text, match):
	"""Handle 2 forms of channel messages."""
	who = match.group("who")
	channel_name = match.group("channel_name")
	msg = match.group("msg").strip()
	if msg.startswith(".") and msg[1:] != "":
		msg = msg[1:]
		r = parser.match(msg)
		if r:
			send_channel(channel_name, r)

@m.trigger(r"""(?P<name>[a-zA-Z]+) tells you\, \'(?P<message>.+)\'""")
def tell_received(t, match):
	"""Trigger that fires when a tell is received."""
	who = match.group("name")
	msg = match.group("message")
	r = parser.match(msg)
	if r:
		tell(who, r)



@m.trigger(r"""Enter Selection\s*->\s*""")
def login_menu(t, match):
	"""Encountered the login menu; send 1 to enter the game"""
	print("Login menu encountered.")
	m.send("1")
	m.send("set cprefix chn:")
	m.send("look")

@m.trigger(r"""^kxwt_supported$""")
def kxwt_support(t, match):
	"""Enable kxwt messages and set up global dictionaries that will store kxwt values."""
	print("Kxwt is supported; enabling")
	m.send("set kxwt on")
	m.g['kxwt'] = {}

@m.trigger(r"""^kxwt_prompt (?P<hp>-{0,1}\d+) (?P<max_hp>-{0,1}\d+) (?P<mana>-{0,1}\d+) (?P<max_mana>-{0,1}\d+) (?P<movement>-{0,1}\d+) (?P<max_movement>-{0,1}\d+)""")
def handle_prompt(text, match):
	"""Parse and store the prompt values we're sent, so that other code has access to them."""
	if m.g['kxwt'].get('stats', None) == None:
		m.g['kxwt']['stats'] = {}
	m.g['kxwt']['stats']['mana'] = match.group("mana")
	m.g['kxwt']['stats']['max_mana'] = match.group("max_mana")
	m.g['kxwt']['stats']['hp'] = match.group("hp")
	m.g['kxwt']['stats']['max_hp'] = match.group("max_hp")
	m.g['kxwt']['stats']['movement'] = match.group("movement")
	m.g['kxwt']['stats']['max_movement'] = match.group("max_movement")

@m.trigger(r"""^kxwt_context (?P<context>.+)\s*""")
def context_handler(text, match):
	"""Handle kxwt context messages by storing them so other code has access to the current context."""
	m.g['kxwt']['context'] = match.group("context").strip()



@m.timer(seconds=1)
def process_send_queue	():
	"""Timer that sends items in the send queue if the character has enough movement."""
	if m.g['kxwt']['stats']['movement'] >= 10: # we can send something
		if m.g['send_queue'] and m.g['kxwt']['context'] == "none": # if there is at least one item in the queue
			i = m.g['send_queue'].popleft()
			if isinstance(i, utils.tell) or isinstance(i, utils.channel_message):
				for l in i.lines_to_send():
					m.send(l)
			else: # just a string, then
				m.send(i)

def run():
	"""Run the test bot"""
	print("Connecting...")
	m.connect()
	print("Logging in...")
	m.login()
	print("Logged in.")

	m.g['kxwt'] = {}
	m.g['kxwt']['context'] = "none" # not a typo
	m.g['kxwt']['stats'] = {}
	m.g['kxwt']['stats']['mana'] = 0
	m.g['kxwt']['stats']['max_mana'] = 0
	m.g['kxwt']['stats']['hp'] = 0
	m.g['kxwt']['stats']['max_hp'] = 0
	m.g['kxwt']['stats']['movement'] = 0
	m.g['kxwt']['stats']['max_movement'] = 0

	m.g['mudmail_queue'] = deque()
	m.g['send_queue'] = deque()
	m.g['rate_limit'] = {}
	m.g['run_commands'] = {}
	m.g['who_list'] = []
	m.g['who_list_players'] = []
	m.send(" ")
	m.send("set kxwt on")
	m.start_processing(True)

if __name__ == '__main__':
	try:
		run()
	except KeyboardInterrupt:
		m.send("quit")
		m.scheduler.shutdown()
