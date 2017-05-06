groupSymbols = {"(": ")", "[": "]", "{": "}"}


def setZero(d):
		for s in d:
			d[s] = 0

def zeroCount(d):
	for v in d.itervalues():
		if v > 0:
			return False
	return True

def splitParse(text, delim=","):
	if text == "":
		return []
	args = []
	symbolCount = groupSymbols.copy()
	setZero(symbolCount)
	temp = ""
	for t in text:
		for k, v in groupSymbols.iteritems():
			if t == k:
				symbolCount[t] += 1
			if t == v:
				symbolCount[k] -= 1
		if t == delim and zeroCount(symbolCount):
			args.append(temp.strip())
			setZero(symbolCount)
			temp = ""
		else:
			temp += t
	if temp:
		args.append(temp.strip())
	return args