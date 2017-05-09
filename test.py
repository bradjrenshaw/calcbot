import parsing
import commands

info = {'name': 'calc', 'version': 0.1}

parser = parsing.parser(None, commands=commands.commands, info=info)


while True:
	text = raw_input("> ")
	print(parser.match(text))