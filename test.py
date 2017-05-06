from commands import *

while True:
	text = raw_input("> ")
	print(parser.match(text))