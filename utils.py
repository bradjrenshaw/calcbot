# utilities

import textwrap
import datetime
import string
import random
import requests

def list_to_string(l):
	"""Given a list of strings, return a proper list, including 'and' commas, etc."""
	if len(l) >= 3:
		l[-1] = """ and {}.""".format(l[-1])
		s = ", ".join(l[:-1])
		s = s + l[-1]
		return s
	elif len(l) == 2:
		s = """{}, {}.""".format(l[0], l[1])
		return s
	elif len(l) == 1:
		s = """{}.""".format(l[-1])
		return s


class mudmail(object):
	def __init__(self, to, subject, message):
		self.to = to
		self.subject = subject
		self.message = message

	def lines_to_send(self):
		lines = []
		lines.append("""mudmail send {}""".format(self.to))
		lines.append("""{}""".format(self.subject))
		for line in self.message.splitlines():
			lines.append(line)
		lines.append("""/done""")
		return lines


class tell(object):
	"""Represents a tell (or multiple tells, if given a long message)."""
	def __init__(self, to, message):
		self.to = to
		self.message = message

	def lines_to_send(self):
		if len(self.message) > 490:
			chunks = textwrap.wrap(self.message, width=490)
			lines = []
			for c in chunks:
				lines.append("""tell {} {}""".format(self.to, c))
			return lines
		else:
			return ["""tell {} {}""".format(self.to, self.message)]

class channel_message(object):
	"""Represents a channel message; handles splitting up of long messages as well."""
	def __init__(self, channel_name, message):
		self.channel_name = channel_name
		self.message = message

	def lines_to_send(self):
		"""Return a list of lines to send."""
		chunks = textwrap.wrap(self.message, width=490)
		lines = []
		for c in chunks:
			lines.append("""channel send {} {}""".format(self.channel_name, c))
		return lines

def rate_limit_check(d, who):
	"""Function to check if the provided name has run a command in the past few seconds"""
	if d.get(who, None) == None: # no entry for this person in the ratelimit dict
		create_rate_limit_dict(d, who)
	if d[who]['banned']:
		return False
	if d[who].get('last_time', None) == None or (datetime.datetime.utcnow() - d[who]['last_time']).total_seconds() > 3: # the last time this person sent a command was more than 3 seconds ago
		d[who]['last_time'] = datetime.datetime.utcnow()
		return True # they can run a command
	else: # it hasn't been 3 seconds since their last command
		d[who]['last_time'] = datetime.datetime.utcnow()
		if d[who]['failed_commands'] >= 15:
			d[who]['banned'] = True
		return False

def create_rate_limit_dict(d, who):
	"""Create the dict for rate_limiting users."""
	d[who] = {}
	d[who]['banned'] = False
	d[who]['ban_notified'] = False
	d[who]['failed_commands'] = 0
	d[who]['warned'] = False

def random_string(size, lowercase=True, uppercase=False):
	"""Return a string according to the lowercase and uppercase args. One must be specified, either way, the return value will be a string of alphanumeric chars"""
	chars = string.digits
	if lowercase:
		chars += string.lowercase
	if uppercase:
		chars += string.uppercase
	return ''.join(random.choice(chars) for i in range(size))

def add_missing_timestamps(session, models):
	"""Add timestamps for every mmodel instance in models that don't have them."""
	updated = 0
	for m in models:
		records = session.query(m).filter(m.added_on==None) # get all rows that have added_on set to none / null
		for r in records:
			# no need to check if they have no timestamp; if they're in the list then they don't
			r.added_on = datetime.datetime.utcnow()
			session.add(r)
			updated += 1
	return updated

def list_bans(m):
	"""Given a mudbot framework object, list the payers that have been banned, if any."""
	b = []
	for name, dict in m.g['rate_limit'].iteritems():
		if dict['banned']:
			b.append(name)
	return b

def alter_aeon_player_exists(player_name):
	"""Return true if the given player name is an alter aeon character, false if otherwise."""
	r = requests.get("https://alteraeon.com:8081/xml/player/{}".format(player_name))
	if r.status_code == 200:
		return True # player exists
	else:
		return False
