import sympy
from parsing import command

def equation(expr):
	"""Converts an equation of the form a+b = c+d into a form sympy can manipulate, in this case c+d-a-b."""
	split = expr.find("=")
	if split < 0:
		raise SyntaxError("Invalid equation syntax.")
	ls = sympy.sympify(expr[:split].strip())
	rs = sympy.sympify(expr[split+1:].strip())
	return rs-ls

def solve_for(expr, variable):
	try:
		expr = equation(expr)
		s = sympy.symbols(variable)
		return str(sympy.solveset(expr, s))
	except:
		return "Incorrect equation syntax."
solve_cmd = command("solve", arguments=["expr", ("variable", "x")], run=solve_for, help="Solves the specified equation for the specified variable.")

def say_func(text):
	return text
say = command("say", arguments=["text"], run=say_func)

def factor_polynomial(expr):
	try:
		expr = sympy.sympify(expr)
		return str(sympy.factor(expr))
	except:
		return "Invalid expression syntax."
factor = command("factor", arguments=["expr"], run=factor_polynomial, help="Factors a polynomial with rational coefficients.")

def eval_func(expr):
	try:
		expr = sympy.sympify(expr)
		return str(expr)
	except:
		return "Invalid expression syntax."
eval_cmd = command("eval", arguments=["expr"], run = eval_func, help="Evaluate an algebraic expression.")

def calc_func(expr):
	try:
		expr = sympy.sympify(expr)
		return str(float(expr))
	except:
		return "Could not convert expression to float."
calc = command("calc", arguments=["expr"], run = calc_func, help="Evaluates an expression and returns the float evaluation.")

def roots_func(expr):
	try:
		expr = sympy.sympify(expr)
		return str(sympy.roots(expr))
	except:
		return "Invalid expression syntax."
roots_cmd = command("roots", arguments=["expr"], run = roots_func, help="Return the roots of an equation.")

def simplify_func(expr):
	print(expr)
	try:
		expr = sympy.sympify(expr)
		return str(sympy.simplify(expr))
	except:
		return "Invalid expression syntax."
simplify_cmd = command("simplify", arguments=["expr"], run=simplify_func, help="Siplifies the given expression.")

class help_command(command):
	def __init__(self, name="help", arguments=[("topic",)], run=None, syntax=None, help="Type help <function> for help on a specific function.", parser=None):
		super(help_command, self).__init__(name, arguments, run, syntax, help, parser)

	def run(self, topic=None):
		print("Topic is {}.".format(topic))
		if not topic:
			msg = "Welcome to {name}, version {version}. ".format(**self.parser.info)
			msg += "Available commands: "+", ".join(self.parser.commands.keys())+"."
			return msg
		else:
			cmd = self.parser.get_command_by_name(topic.lower())
			if not cmd:
				return "Command {} not found.".format(topic.lower())
			else:
				return cmd.help+" "+cmd.syntax

help_cmd = help_command()

commands = {
	'help': help_cmd,
	'solve': solve_cmd,
	'factor': factor,
	'eval': eval_cmd,
	'calc': calc,
	'roots': roots_cmd,
	'simplify': simplify_cmd,
}