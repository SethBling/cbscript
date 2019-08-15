import copy
from scratch_tracker import scratch_tracker
from CompileError import CompileError

'''
{C for color
{U for underline, {u to exit underline, same for {D bold, {S strikethrough and {I italic
{- to clear formatting
[text](command) for a command click event
[text](http://url) for a url link click event
[text](//command) for a command suggestion click event
(@Selector) to display a selector name
(@Selector.Score) to display a score
(Score) to display a Global score.
'''

def getPropertiesText(properties):
	text = ""
	if properties["color"] <> None:
		text = text + ',"color":"' + properties["color"] + '"'
	if properties["bold"]:
		text = text + ',"bold":true'
	if properties["underlined"]:
		text = text + ',"underlined":true'
	if properties["italic"]:
		text = text + ',"italic":true'
	if properties["strikethrough"]:
		text = text + ',"strikethrough":true'
		
	return text
		
def formatJsonText(func, text):
	formatted = '[""'
	local_scratch = []
	
	for segment, properties in parseTextFormatting(text):
		propertiesText = getPropertiesText(properties)
		if isinstance(segment, basestring):
			formatted = formatted + ',{{"text":"{0}"{1}}}'.format(segment.replace('"', '\\"'), getPropertiesText(properties))
		else:
			unformatted, command = segment
			if unformatted == None:
				parts = command.split(".")
				if len(parts) > 2:
					raise CompileError('Json text has invalid () text: "{}"'.format(command))
				if len(parts) == 1:
					if len(parts[0]) == 0:
						raise CompileError('Empty () in json text.')
					if parts[0][0] == '@':
						formatted = formatted + ',{{"selector":"{0}"{1}}}'.format(parts[0],getPropertiesText(properties))
					else:
						formatted = formatted + ',{{"score":{{"name":"Global","objective":"{0}"}}{1}}}'.format(parts[0], getPropertiesText(properties))
				if len(parts) == 2:
					formatted = formatted + ',{{"score":{{"name":"{}","objective":"{}"}}{}}}'.format(parts[0], parts[1], getPropertiesText(properties))
			elif command == None:
				formatted = formatted + ',{{"text":"{0}"{1}}}'.format(unformatted.replace('"', '\\"'), getPropertiesText(properties))
			else:
				command = command.replace('"', '\\"')
				if command.startswith('http'):
					action = 'open_url'
				elif command.startswith('//'):
					action = 'suggest_command'
					command = command[1:]
				elif command.startswith('call '):
					action = 'run_command'
					command = '/function {}:{}'.format(func.namespace, command[len('call '):])
				else:
					action = 'run_command'
				formatted = formatted + ',{{"text":"{0}","clickEvent":{{"action":"{1}","value":"{2}"}}{3}}}'.format(unformatted.replace('"', '\\"'), action, command, getPropertiesText(properties))
			
	formatted = formatted + "]"
	
	for scratch_var in local_scratch:
		func.free_scratch(scratch_var)
	
	return formatted

COLORS = {
	"k": "black",
	"K": "dark_gray",
	"w": "gray",
	"W": "white",
	"r": "dark_red",
	"R": "red",
	"g": "dark_green",
	"G": "green",
	"b": "dark_blue",
	"B": "blue",
	"y": "gold",
	"Y": "yellow",
	"c": "dark_aqua",
	"C": "aqua",
	"m": "dark_purple",
	"M": "light_purple",
}
	
def parseTextFormatting(text):
	NONE = 1
	FORMATTED = 2
	ENDFORMATTED = 3
	COMMAND = 4
	SCOREBOARD = 5
	PROPERTY = 6

	escaped = False
	
	mode = NONE
	seg = ""
	formatted = ""
	
	segments = []
	properties = {"color": None, "bold": False, "underlined": False, "italic": False, "strikethrough": False}
	
	for ch in text:
		if ch == "\\" and not escaped:
			escaped = True
		elif escaped:
			seg = seg + ch
			escaped = False
		elif mode == NONE:
			if ch == "[":
				if len(seg) > 0:
					segments.append((seg, copy.copy(properties)))
					seg = ""
				mode = FORMATTED
			elif ch == "(":
				if len(seg) > 0:
					segments.append((seg, copy.copy(properties)))
					seg = ""
				mode = SCOREBOARD
			elif ch == "{":
				if len(seg) > 0:
					segments.append((seg, copy.copy(properties)))
					seg = ""
				mode = PROPERTY
			else:
				seg = seg + ch
		elif mode == FORMATTED:
			if ch == "]":
				formatted = seg
				seg = ""
				mode = ENDFORMATTED
			else:
				seg = seg + ch
		elif mode == ENDFORMATTED:
			if ch == "(":
				mode = COMMAND
			else:
				segments.append(((formatted, None), copy.copy(properties)))
				formatted = ""
				mode = NONE
				seg = seg + ch
		elif mode == COMMAND:
			if ch == ")":
				segments.append(((formatted, seg), copy.copy(properties)))
				seg = ""
				formatted = ""
				mode = NONE
			else:
				seg = seg + ch
		elif mode == SCOREBOARD:
			if ch == ")":
				segments.append(((None, seg), copy.copy(properties)))
				seg = ""
				mode = NONE
			else:
				seg = seg + ch
		elif mode == PROPERTY:
			if ch in COLORS:
				properties["color"] = COLORS[ch]
			elif ch == "-":
				properties["color"] = None
				properties["bold"] = False
				properties["underlined"] = False
				properties["italic"] = False
				properties["strikethrough"] = False
			elif ch == "D":
				properties["bold"] = True
			elif ch == "d":
				properties["bold"] = False
			elif ch == "U":
				properties["underlined"] = True
			elif ch == "u":
				properties["underlined"] = False
			elif ch == "I":
				properties["italic"] = True
			elif ch == "i":
				properties["italic"] = False
			elif ch == "S":
				properties["strikethrough"] = True
			elif ch == "s":
				properties["strikethrough"] = False
			elif ch == "{":
				seg = seg + ch
			else:
				raise CompileError('Unexpected formatting character {{{0} in tell command'.format(ch))
			
			mode = NONE
	
	if len(seg) > 0:
		segments.append((seg, copy.copy(properties)))
				
	return segments