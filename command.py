import parsing

class command(object):
	def __init__(self, name, arguments=None, run=None, syntax=None, help="No help message provided.", parser=None):
		self.name = name
		self.help = help
		self.arguments = arguments
		if run:
			self.run = run
		self._syntax = syntax
		self.parser = parser

	def get_argument(self, index):
		arg = self.arguments[index]
		if type(arg) == str:
			return (arg, None)
		if type(arg) == list or type(arg) == tuple:
			if len(arg) >= 2:
				return arg
			else:
				return (arg[0], None)
		raise TypeError("Invalid argument type {}.".format(type(arg)))

	def match_arguments(self, args):
		newargs = []
		for x in range(len(self.arguments)):
			try:
				newargs.append(args[x])
			except:
				if type(self.arguments[x]) == str:
					return None
				name, default = self.get_argument(x)
				if default:
					newargs.append(default)
		return newargs

	def parse(self, text):
		"""Parses the given text into component arguments, delimited by commas then passes the result to the run function."""
		print "Text is ", text
		args = parsing.splitParse(text)
		print "Args is now", args
		args = self.match_arguments(args)
		if args == None: #None specifically means syntax error, not an empty list.
			return self.syntax
		return self.run(*args)

	def run(self, *args):
		"""Handles parsing and command execution."""
		pass

	@property
	def syntax(self):
		if not self._syntax:
			sargs = []
			for s in self.arguments:
				if type(s) == list or type(s) == tuple:
					sargs.append("[{}, default={}]".format(*s) if len(s)>=2 else "[{}]".format(s[0]))
				if type(s) == str:
					sargs.append(s)
			return "Syntax: "+self.name+" "+", ".join(sargs)
		return self._syntax

class parser(object):
	def __init__(self, bot, commands=None, info=None):
		self.bot = bot #The mbf instance.
		self.commands = commands if commands else {}
		self.info = info

	def add(self, cmd):
		"""Returns true if there were no conflicts, otherwise false."""
		if not isinstance(cmd, command):
			return False
		if cmd.name in self.commands:
			return False
		self.commands[cmd.name] = cmd
		cmd.parser = self
		return True

	def get_command_by_name(self, name):
		if name in self.commands:
			return self.commands[name]
		return None

	def parse(self, text):
		"""Splis a command into the name of the command and the string of args. If this fails, None is returned."""
		space = text.find(" ")
		if space >= 0 and space < len(text)-1:
			cmd = text[0:space]
			args = text[space+1:]
			return (cmd, args)
		return (text, "")

	def run(self, cmd, arguments):
		if cmd in self.commands:
			return self.commands[cmd].parse(arguments)
		return "{} is not a valid command.".format(cmd)

	def match(self, text):
		e = self.parse(text)
		if e:
			return self.run(e[0], e[1])