# TODO: Place sign at beginning labelling the script
# TODO: Add "function" sections that can be triggered once by a call. Set redstone_block and set stone in the same tick.
# TODO: Make gamerule block use the CBarmorstand
# TODO: Make compile error for objectives longer than 16 characters
# TODO: Make global variables that are stored on the main armor stand

import sys
sys.path.append("./pymclevel")
import mclevel
import os
import os.path
import time
from nbt import TAG_Compound
from nbt import TAG_String
from nbt import TAG_Int
from nbt import TAG_Byte
from nbt import TAG_List
from nbt import TAG_Value
import copy
import math
import random
import scriptparse
import collections
import traceback
import copy

if len(sys.argv) <> 2:
	print "You must include a script filename."
	exit()
	
scriptFilename = sys.argv[1]
script = {}

IMPULSE = 137
CHAIN = 211
REPEATING = 210

AUTO = 2
DEFAULTON = 1
DEFAULTOFF = 0

def addCommandBlock(level, type, x, y, z, command):
	data = 3
	powered = 0
	
	if len(command) >= 1 and command[0] == '>':
		data = data + 8
		command = command[1:]

	if len(command) >= 1:
		if command[0] == '-':
			level.setBlockAt(x-1, y, z, 1) #Stone
			level.setBlockDataAt(x-1, y, z, 0)

		if command[0] == '+':
			level.setBlockAt(x-1, y, z, 152) # Redstone Block
			level.setBlockDataAt(x-1, y, z, 0)
			powered = 1
	
		if command[0] in '-+':
			auto = 0
			command = command[1:]
		else:
			auto = 1

	chunk = level.getChunk(x/16, z/16)
	te = level.tileEntityAt(x, y, z)
	if te != None:
		chunk.TileEntities.remove(te)
	control = TAG_Compound()
	control["Command"] = TAG_String(command)
	control["id"] = TAG_String(u'minecraft:command_block')
	control["CustomName"] = TAG_String(u'@')
	control["SuccessCount"] = TAG_Int(0)
	control["powered"] = TAG_Byte(powered)
	control["x"] = TAG_Int(x)
	control["y"] = TAG_Int(y)
	control["z"] = TAG_Int(z)
	if type == CHAIN:
		control["auto"] = TAG_Byte(auto)
	else:
		control["auto"] = TAG_Byte(0)
	control["TrackOutput"] = TAG_Byte(0)
	chunk.TileEntities.append(control)
	chunk.dirty = True
	level.setBlockAt(x, y, z, type)
	level.setBlockDataAt(x, y, z, data)
	
	chunk.dirty = True


def updateScript():
	modified = time.ctime(os.path.getmtime(scriptFilename))
	if script == {}:
		script["path"] = scriptFilename
		script["modified"] = modified
		with open(scriptFilename, 'r') as content_file:
			script["text"] = content_file.read()
		script["applied"] = False
		
		print "Loaded script: " + script["path"]
	elif script["modified"] < modified:
		with open(scriptFilename, 'r') as content_file:
			script["text"] = content_file.read()
		script["applied"] = False
		script["modified"] = modified

def writeFunction(context, level, x, y, z, commands):
	# Open file
	for command in commands:
		addCommandBlock(level, CHAIN, x, y, z+pos, command)
				
def friendlyName(script):
	name = "CB" + os.path.basename(script["path"]).split('.')[0][:14]
	name = name.replace(' ', '_')
	name = name.replace('.', '_')
	name = name.replace(',', '_')
	name = name.replace(':', '_')
	name = name.replace('{', '_')
	name = name.replace('}', '_')
	name = name.replace('=', '_')
	
	return name

# Gets the name of the objective for the rand() arithmetic function
def randomObjective(context):
	name = context["name"]
	
	return "RV" + name[2:]

def addTick(level, x, y, z, timer, identifier):
	buttonTick = TAG_Compound()
	buttonTick["p"] = TAG_Int(0)
	buttonTick["t"] = TAG_Int(timer)
	buttonTick["i"] = TAG_String(identifier)
	buttonTick["x"] = TAG_Int(x)
	buttonTick["y"] = TAG_Int(y)
	buttonTick["z"] = TAG_Int(z)
	chunk = level.getChunk(x/16, z/16)
	levelTag = chunk.root_tag["Level"]
	if "TileTicks" not in levelTag:
		levelTag["TileTicks"] = TAG_List()
	chunk.root_tag["Level"]["TileTicks"].append(buttonTick)
	chunk.dirty = True
		
def applyScript(script):
	result = scriptparse.parse(script["text"] + "\n")
	
	if result == None:
		print "Unable to parse script."
		return False
	
	type, parsed = result
	
	if type <> 'program':
		print "Script does not contain a full program."
		return False
	
	context = {}
	context["script"] = script
	context["scratch"] = 0
	context["temp"] = 0
	context["constants"] = []
	context["gamerules"] = {}
	context["objectives"] = {}
	context["rand"] = 0
	context["name"] = friendlyName(script)
	context["sections"] = {}
	context["placed"] = []
	context["triggers"] = {}
	context["auto"] = AUTO

	environment = {}
	environment["__qualifiers"] = ""

	filename = parsed["file"]
	lx, ly, lz = parsed["at"]

	context["sections"]["reset"] = {}
	context["sections"]["reset"]["pos"] = (lx, ly, lz)
	context["sections"]["reset"]["commands"] = []
	context["sections"]["reset"]["gamerules"] = {}
	context["sections"]["reset"]["type"] = "reset"
	
	dy = 0
	for type, name, _ in parsed["sections"]:
		if name == "reset":
			continue
			
		if name in context["sections"]:
			print "Duplicate section name '{0}'".format(name)
			return False
			
		dy = dy + 1
		context["sections"][name] = {}
		context["sections"][name]["pos"] = (lx, ly+dy, lz)
		context["sections"][name]["commands"] = []		
		context["sections"][name]["gamerules"] = {}
		context["sections"][name]["type"] = type
	
	if not compile(context, parsed["assignments"], environment):
		print "Could not compile assignments."
		return False
	
	for type, name, blocks in parsed["sections"]:
		context["section"] = name
		if not compile(context, blocks, environment):
			print "Could not compile '{0}' section.".format(name)
			return False
	
	try:
		level = mclevel.fromFile(filename)
	except:
		print "Unable to read world file."
		return False
	
	if parsed["dim"]:
		level = level.getDimension(parsed["dim"])
	
	context["section"] = "reset"
	for s in xrange(context["scratch"]):
		addCommand(context, environment, "/scoreboard objectives add scratch" + str(s) + " dummy")
	
	for t in xrange(context["temp"]):
		addCommand(context, environment, "/scoreboard objectives add temp" + str(t) + " dummy")
		
	if len(context["constants"]) > 0:
		addCommand(context, environment, "/scoreboard objectives add Constant dummy")
		for c in context["constants"]:
			if c == -1:
				addCommand(context, environment, "/scoreboard players set minus Constant -1")
			else:
				addCommand(context, environment, "/scoreboard players set c" + str(c) + " Constant " + str(c))
	
	if context["rand"] > 0:
		addCommand(context, environment, '/kill @e[type=armor_stand,name=RandBasis,score_{0}_min=0]'.format(randomObjective(context)))
		addCommand(context, environment, "/scoreboard objectives add {0} dummy".format(randomObjective(context)))
		for i in xrange(context["rand"]):
			addCommand(context, environment, '/summon armor_stand ~1 ~ ~ {CustomName:"RandBasis", Invulnerable:1, Marker:1, NoGravity:1}')
			addCommand(context, environment, '/scoreboard players add @e[type=armor_stand,name=RandBasis] {0} 1'.format(randomObjective(context)))
		addCommand(context, environment, '/scoreboard players remove @e[type=armor_stand,name=RandBasis] {0} 1'.format(randomObjective(context)))
	
	for gamerule in context["gamerules"].keys():
		addCommand(context, environment, "/scoreboard objectives add GR{0} dummy".format(gamerule))
	
	for section in context["sections"].keys():
		for gamerule in context["sections"][section]["gamerules"].keys():
			context["sections"][section]["commands"].insert(0, "/scoreboard players set @a GR{0} 0".format(gamerule))
			context["sections"][section]["commands"].insert(1, "/stats entity @a set QueryResult @p[r=1] GR{0}".format(gamerule))
			context["sections"][section]["commands"].insert(2, "/execute @a ~ ~ ~ /gamerule {0}".format(gamerule))
			context["sections"][section]["commands"].insert(3, "/stats entity @a clear QueryResult")

	createRegisteredObjectives(context, trigger = True)
	createRegisteredObjectives(context)
	
	context["sections"]["reset"]["commands"].insert(0, "/kill @e[type=armor_stand,name={0}]".format(context["name"]))
	context["sections"]["reset"]["commands"].insert(1, '/summon armor_stand ~ ~ ~-4 {{CustomName:"{0}", Marker:1b, Invisible:1b, NoGravity:1b, Invulnerable:1b}}'.format(context["name"]))
	
	context["section"] = "reset"
	
	for section in context["sections"].keys():
		commands = context["sections"][section]["commands"]
		type = context["sections"][section]["type"]
		
		if type == "clock":
			addCommandBlock(level, REPEATING, x, y, z+1, "")
			writeFunction(context, level, x, y, z+2, commands)
		elif type == "function":
			addCommandBlock(level, IMPULSE, x, y, z+1, "")
			writeFunction(context, level, x, y, z+2, commands)
		elif type == "reset":
			addCommandBlock(level, IMPULSE, x, y, z+1, "/setblock ~-1 ~ ~-1 air")
			addCommandBlock(level, CHAIN, x, y, z+2, "/say Resetting script.")
			writeFunction(context, level, x, y, z+3, commands)
		else:
			print "Unknown block type: '{0}'".format(type)
			return False
			
	try:
		level.saveInPlace()
		level.close()
	except:
		print "Unable to write world file."
		return False
	
	return True

def createRegisteredObjectives(context, trigger = False):
	existing = {}
	defineStr = "/scoreboard objectives add " 
	for cmd in context["sections"]["reset"]["commands"]:
		if cmd[:len(defineStr)] == defineStr:
			existing[cmd[len(defineStr):].split(' ')[0]] = True
	
	if trigger:
		objectives = context["triggers"].keys()
	else:
		objectives = context["objectives"].keys()
		
	for objective in objectives:
		if objective not in existing:
			if trigger:
				context["sections"]["reset"]["commands"].insert(0, "/scoreboard objectives add {0} trigger".format(objective))
			else:
				context["sections"]["reset"]["commands"].insert(0, "/scoreboard objectives add {0} dummy".format(objective))
	
def interpretSelectors(line, qualifiers, context):
	fragments = []
	
	text = ""
	selector = False
	skip = 0
	for i in xrange(len(line)):
		if i+2<len(line):
			triplet = line[i:i+3]
			if triplet in ["@a[", "@p[", "@e[", "@r["]:
				selector = True
				fragments.append(text)
				text = ""
		if not selector and i+1<len(line):
			doublet = line[i:i+2]
			if doublet in ["@a", "@p", "@e", "@r"]:
				fragments.append(text)
				text = ""
				fragments.append(doublet)
				skip = 2
		
		if skip > 0:
			skip = skip - 1
		else:
			text += line[i]
		
		if selector and line[i] == "]":
			selector = False
			fragments.append(text)
			text = ""
	fragments.append(text)
			
	interpreted = ""
	
	for fragment in fragments:
		if len(fragment) > 0 and fragment[0] == '@':
			sel = interpretSelector(fragment, qualifiers, context)
			if sel == None:
				return None
			interpreted += sel
		else:
			interpreted += fragment
	
	return interpreted

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def interpretSelector(selector, qualifiers, context):
	if len(selector) == 2:
		selector += "[]"
	
	start = selector[0:3]
	end = selector[-1]
	middle = selector[3:-1]
	if qualifiers <> "":
		middle = combineLists(qualifiers, middle)
	parts = middle.split(',')
	
	if len(parts) == 0:
		return selector[0:2]
	
	interpreted = start
	newParts = []
	for part in parts:
		part = part.strip()
		if len(part) == 0:
			continue
			
		if '==' in part:
			before,after = tuple(part.split('==', 1))
			before = before.strip()
			after = after.strip()
			if not isNumber(after):
				print "'" + str(after) + "' is not a number"
				return None
			newParts.append("score_{0}_min={1}".format(before, after))
			newParts.append("score_{0}={1}".format(before, after))
			registerObjective(context, before)
		elif '<=' in part:
			before,after = tuple(part.split('<=', 1))
			before = before.strip()
			after = after.strip()
			if not isNumber(after):
				print "'" + str(after) + "' is not a number"
				return None
			newParts.append("score_{0}={1}".format(before, after))
			registerObjective(context, before)
		elif '>=' in part:
			before,after = tuple(part.split('>=', 1))
			before = before.strip()
			after = after.strip()
			if not isNumber(after):
				print "'" + str(after) + "' is not a number"
				return None
			newParts.append("score_{0}_min={1}".format(before, after))
			registerObjective(context, before)
		elif '<' in part:
			before,after = tuple(part.split('<', 1))
			before = before.strip()
			after = after.strip()
			if not isNumber(after):
				print "'" + str(after) + "' is not a number"
				return None
			newParts.append("score_{0}={1}".format(before, int(after)-1))
			registerObjective(context, before)
		elif '>' in part:
			before,after = tuple(part.split('>', 1))
			before = before.strip()
			after = after.strip()
			if not isNumber(after):
				print "'" + str(after) + "' is not a number"
				return None
			newParts.append("score_{0}_min={1}".format(before, int(after)+1))
			registerObjective(context, before)
		elif '=' not in part and not isNumber(part):
			if len(part) >= 5 and part[:4].upper() == "NOT ":
				newParts.append("score_{0}=0".format(part[4:]))
				registerObjective(context, part[4:])
			else:
				newParts.append("score_{0}_min=1".format(part))
				registerObjective(context, part)
		else:
			newParts.append(part)
	
	interpreted += ','.join(newParts)
	interpreted += end
	
	if len(interpreted) == 4:
		# We have @a[] or similar, so truncate
		interpreted = interpreted[:2]
	
	return interpreted
	
def removeEmpty(list):
	ret = []
	for item in list:
		if item <> "":
			ret.append(item)
	
	return ret
	
def combineLists(l1, l2):
	return ",".join(removeEmpty(l1.split(",")) + removeEmpty(l2.split(",")))
	
def addCommand(context, environment, command):
	if "__prefix" in environment:
		command = environment["__prefix"] + command
		
	command = applyEnvironment(command, environment)
	command = interpretSelectors(command, environment["__qualifiers"], context)
	
	if context["auto"] == DEFAULTOFF:
		command = "-" + command
	if context["auto"] == DEFAULTON:
		command = "+" + command
	
	context["sections"][context["section"]]["commands"].append(command)
	
	return len(context["sections"][context["section"]]["commands"]) - 1

def addConditionalCommand(context, environment, command):
	command = applyEnvironment(command, environment)
	command = interpretSelectors(command, environment["__qualifiers"], context)
	
	context["sections"][context["section"]]["commands"].append(">" + command)
	
	return len(context["sections"][context["section"]]["commands"]) - 1

def registerObjective(context, objective):
	if objective[:6] == "score_":
		objective = objective[6:]
	if objective[-4:] == "_min":
		objective = objective[:-4]
	
	context["objectives"][objective] = True
	
def getTempVar(scratch):
	for key in scratch["temp"].keys():
		if scratch["temp"][key] == False:
			scratch["temp"][key] = True
			return "temp" + str(key)
	
	newScratch = len(scratch["temp"].keys())
	scratch["temp"][newScratch] = True
	return "temp" + str(newScratch)

def freeTempVar(scratch, id):
	num = int(id[4:])
	
	scratch["temp"][num] = False


def getScratch(scratch):
	for key in scratch["scratch"].keys():
		if scratch["scratch"][key] == False:
			scratch["scratch"][key] = True
			return "scratch" + str(key)
	
	newScratch = len(scratch["scratch"].keys())
	scratch["scratch"][newScratch] = True
	return "scratch" + str(newScratch)

def isScratch(id):
	return len(id) >= 7 and id[:7] == "scratch"
	
def freeScratch(scratch, id):
	if not isScratch(id):
		return

	num = int(id[7:])
	
	scratch["scratch"][num] = False
		
def addOperation(context, environment, selector, id1, operation, id2):
	if "c=1" in selector:
		addCommand(context, environment, "/scoreboard players operation {4} {1} {2} {4} {3}".format(selector, id1, operation, id2, combineSelectors(selector, "[c=1]")))
	else:
		addCommand(context, environment, "/execute {0} ~ ~ ~ /scoreboard players operation {4} {1} {2} {4} {3}".format(selector, id1, operation, id2, combineSelectors(selector, "[c=1]")))

def addConstant(context, c):
	if c not in context["constants"]:
		context["constants"].append(c)
	
	return "c" + str(c)
	
def factor(n):
    i = 2
    limit = math.sqrt(n)    
    while i <= limit:
      if n % i == 0:
        yield i
        n = n / i
        limit = math.sqrt(n)   
      else:
        i += 1
    if n > 1:
        yield n
		
def combineSelectors(selector, qualifiers):
	if selector[-1] <> ']':
		return selector + qualifiers
	else:
		return selector[:-1] + "," + qualifiers[1:]

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
		
def formatJsonText(text, context, environment):
	scratch = {"scratch": {}, "temp": {}}
	formatted = '[""'
	
	for segment, properties in parseTextFormatting(text):
		propertiesText = getPropertiesText(properties)
		if isinstance(segment, basestring):
			formatted = formatted + ',{{"text":"{0}"{1}}}'.format(segment.replace('"', '\\"'), getPropertiesText(properties))
		else:
			unformatted, command = segment
			if unformatted == None:
				parts = command.split(".")
				if len(parts) > 2:
					continue
				if len(parts) == 1:
					formatted = formatted + ',{{"selector":"{0}"{1}}}'.format(parts[0],getPropertiesText(properties))
				if len(parts) == 2:
					tempId = getScratch(scratch)
					registerObjective(context, tempId)
					addCommand(context, environment, "/scoreboard players reset @a {0}".format(tempId))
					addCommand(context, environment, "/scoreboard players operation @a {0} = {1} {2}".format(tempId, parts[0], parts[1]))
					formatted = formatted + ',{{"score":{{"name":"@p","objective":"{0}"}}{1}}}'.format(tempId, getPropertiesText(properties))
			elif command == None:
				formatted = formatted + ',{{"text":"{0}"{1}}}'.format(unformatted.replace('"', '\\"'), getPropertiesText(properties))
			else:
				formatted = formatted + ',{{"text":"{0}","clickEvent":{{"action":"run_command","value":"{1}"}}{2}}}'.format(unformatted.replace('"', '\\"'), command.replace('"', '\\"'), getPropertiesText(properties))
			
	formatted = formatted + "]"
	
	return formatted

COLORS = {
	"l": "black",
	"L": "dark_gray",
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
	ESCAPED = 7
	
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
			elif ch == "\\":
				mode = ESCAPED
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
				print("Unexpected formatting character {{{0} in tell command".format(ch))
			
			mode = NONE
		elif mode == ESCAPED:
			seg = seg + ch
			mode = NONE
	
	if len(seg) > 0:
		segments.append((seg, copy.copy(properties)))
				
	return segments
	
def calcMath(selector, expr, context, scratch, environment):
	etype = expr[0]
	qualifiers = environment["__qualifiers"]
	if etype == 'VAR':
		registerObjective(context, expr[1])
		return expr[1]
	if etype == 'SELVAR':
		registerObjective(context, expr[2])
		newId = getScratch(scratch)
		registerObjective(context, newId)
		addCommand(context, environment, "/scoreboard players operation {0} {1} = {2} {3}".format(selector, newId, expr[1], expr[2]))
		
		return newId
		
	if etype == 'BINOP':
		type = expr[1]
		if len(type) == 1 and type in "+-*/%":
			if type in "+*" and expr[2][0] == 'NUM' and expr[3][0] <> 'NUM':
				left = expr[3]
				right = expr[2]
			else:
				left = expr[2]
				right = expr[3]
		
			id1 = calcMath(selector, left, context, scratch, environment)
			if id1 == None:
				return None
			
			if not isScratch(id1):
				newId = getScratch(scratch)
				addOperation(context, environment, selector, newId, '=', id1)
				id1 = newId
				
			if right[0] == 'NUM':
				operand2 = right[1]
				if type == '+':
					addCommand(context, environment, "/scoreboard players add {0} {1} {2}".format(selector, id1, operand2))
				elif type == '-':
					addCommand(context, environment, "/scoreboard players remove {0} {1} {2}".format(selector, id1, operand2))
				else:
					id2 = addConstant(context, int(operand2))
					addCommand(context, environment, "/scoreboard players operation {0} {1} {2}= {3} Constant".format(selector, id1, type, id2))
			else:
				id2 = calcMath(selector, right, context, scratch, environment)
				if id2 == None:
					return None
				
				addOperation(context, environment, selector, id1, type+'=', id2)
				if isScratch(id2):
					freeScratch(scratch, id2)
			
			return id1
		if type == "^":
			target = calcMath(selector, expr[2], context, scratch, environment)
			if target == None:
				return None
			power = int(expr[3])
			if power < 1:
				print "Powers less than 1 are not supported"
				return None
				
			if power == 1:
				return target
				
			newId = getScratch(scratch)
			addOperation(context, environment, selector, newId, '=', target)
			
			for i in xrange(power-1):
				addOperation(context, environment, selector, newId, '*=', target)
				
			return newId
		print "Binary operation '{0}' isn't implemented".format(type)
		return None
	if etype == 'GROUP': return calcMath(selector, expr[1], context, scratch, environment)
	if etype == 'NUM': 
		id = getScratch(scratch)
		num = applyEnvironment(expr[1], environment)
		interpreted = interpretSelector(selector, qualifiers, context)
		command = "/scoreboard players set {0} {1} {2}".format(selector, id, num)
		addCommand(context, environment, command)
		
		return id
	if etype == 'UNARY':
		type = expr[1]
		if type == "-":
			id = calcMath(selector, expr[2], context, scratch, environment)
			if id == None:
				return None
			if not isScratch(id):
				newId = getScratch(scratch)
				addOperation(context, environment, selector, newId, '=', id)
				id = newId

			addConstant(context, -1)
			addCommand(context, environment, "/scoreboard players operation {0} {1} *= minus Constant".format(selector, id))
			
			return id
		
		
		print "Unary operation '{0}' isn't implemented.".format(type)
		return None
			
	if etype == 'FUNC':
		func = expr[1]
		args = expr[2]
		
		if func == 'sqrt':
			if len(args) <> 1:
				print "sqrt takes exactly 1 argument, received: {0}".format(args)
				return None
			
			id = calcMath(selector, args[0], context, scratch, environment)
			if id == None:
				return None
			
			guess = calcMath(selector, scriptparse.parse("20")[1], context, scratch, environment)
			if guess == None:
				return None
			for iteration in xrange(7):
				newId = getScratch(scratch)
				addOperation(context, environment, selector, newId, '=', id)
				guess = calcMath(selector, scriptparse.parse("({0}/{1}+{1})/2".format(newId, guess))[1], context, scratch, environment)
				if guess == None:
					return None
			
			return guess

		if func == 'abs':
			if len(args) <> 1:
				print "abs takes exactly 1 argument, received: {0}".format(args)
				return None

			id = calcMath(selector, args[0], context, scratch, environment)
			if id == None:
				return None
			
			if not isScratch(id):
				newId = getScratch(scratch)
				addOperation(context, environment, selector, newId, '=', id)
				id = newId	
		
			addConstant(context, -1)
			command = "/scoreboard players operation {0} {1} *= minus Constant".format(combineSelectors(selector, "[{0} <= -1]".format(id)), id)
			addCommand(context, environment, command)
			
			return id
			
		if func == 'rand':
			if len(args) == 1:
				min = 0
				if args[0][0] == 'NUM':
					max = applyEnvironment(args[0][1], environment)
					if not isNumber(max):
						print "Argument '{0}' to rand is not an integer.".format(args[0][1])
						return None
					max = int(max)
				else:
					print "Function 'rand' accepts only integer arguments."
					return None
			elif len(args) == 2:
				if args[0][0] == 'NUM':
					min = applyEnvironment(args[0][1], environment)
					if not isNumber(min):
						print "Argument '{0}' to rand is not an integer.".format(args[0][1])
						return None
					min = int(min)
				else:
					print "Function 'rand' accepts only integer arguments."
					return None
				if args[1][0] == 'NUM':
					max = applyEnvironment(args[1][1], environment)
					if not isNumber(max):
						print "Argument '{0}' to rand is not an integer.".format(args[1][1])
						return None
					max = int(max)

				else:
					print "Function 'rand' accepts only integer arguments."
					return None
			else:
				print "abs takes exactly 1 argument, received: {0}".format(args)
				return None
				
			range = max - min
			
			if range <= 0:
				print("rand must have a range greater than 0. Provided {0} to {1}.".format(min, max))
				return None

			id = getScratch(scratch)
			addCommand(context, environment, "/scoreboard players set {0} {1} 0".format(selector, id))
			
			first = True
			for f in factor(range):
				if f > context["rand"]:
					context["rand"] = f
				
				if first:
					first = False
				else:
					c = addConstant(context, f)
					addCommand(context, environment, "/scoreboard players operation {0} {1} *= {2} Constant".format(selector, id, c))
				
				addCommand(context, environment, "/execute {0} ~ ~ ~ /scoreboard players operation {4} {1} += @r[type=armor_stand,name=RandBasis,score_{2}={3}] {2}".format(selector, id, randomObjective(context), f-1, combineSelectors(selector, "[c=1]")))
			
			if min <> 0:
				addCommand(context, environment, "/scoreboard players add {0} {1} {2}".format(selector, id, min))
				
			return id

		if func == 'sin' or func == 'cos':
			if len(args) <> 1:
				print "{0} takes exactly 1 argument, received: {1}".format(func, args)
				return None
			
			id = calcMath(selector, args[0], context, scratch, environment)
			if id == None:
				return None
			
			if func == 'sin':
				moddedId2 = calcMath(selector, scriptparse.parse("(({0}%360)+360)%360".format(id))[1], context, scratch, environment)
			else:
				moddedId2 = calcMath(selector, scriptparse.parse("(({0}%360)+450)%360".format(id))[1], context, scratch, environment)
			if moddedId2 == None:
				return None
				
			modId = getTempVar(scratch)
			addOperation(context, environment, selector, modId, '=', moddedId2)
			c180 = addConstant(context, 180)
			addCommand(context, environment, "/scoreboard players operation {0} {1} %= {2} Constant".format(selector, modId, c180))
			
			parsed = scriptparse.parse("4000*{0}*(180-{0})/(40500-{0}*(180-{0}))".format(modId))
			retId = calcMath(selector, parsed[1], context, scratch, environment)
			if retId == None:
				return None
			
			addConstant(context, -1)
			addCommand(context, environment, "/scoreboard players operation {0} {1} *= minus Constant".format(combineSelectors(selector, "[{0} > 180]".format(moddedId2)), retId))
			
			freeTempVar(scratch, modId)
			freeScratch(scratch, moddedId2)
			
			return retId
		
		print "Unknown function '{0}'.".format(func)
		return None
			
	print "Unable to interpret math block."
	
	return None
	
def applyEnvironment(text, environment):
	for identifier in reversed(sorted(environment.keys())):
		if identifier[0] == '@':
			text = text.replace(identifier + "[", environment[identifier][:-1]+",")
			text = text.replace(identifier, environment[identifier])
		else:
			text = text.replace("$" + identifier, str(environment[identifier]))	
		
	return text
	
def compileWithPrefix(context, blocks, environment, prefix):
	prefix = applyEnvironment(prefix, environment)
	prefix = interpretSelectors(prefix, "", context)
	
	subEnvironment = copy.deepcopy(environment)
	if "__prefix" in environment:
		subEnvironment["__prefix"] = environment["__prefix"] + prefix
	else:
		subEnvironment["__prefix"] = prefix
	
	if not compile(context, blocks, subEnvironment):
		return False
		
	return True

def compile(context, blocks, environment):
	for (type, content) in blocks:
		if type == 'Command':
			command = content
			addCommand(context, environment, command)			
			
		elif type == 'For':
			identifier, setpython, sub = content
			
			try:
				set = eval(setpython, globals(), environment)
			except:
				print "Could not evaluate: " + setpython
				return False
			
			try:
				iter(set)
			except:
				print "'{0}' is not an iterable set.".format(setpython)
				return False

			for v in set:
				subEnvironment = copy.deepcopy(environment)
				subEnvironment[identifier] = v
				if not compile(context, sub, subEnvironment):
					return False
		elif type == 'Select':
			selector, sub = content
			
			subEnvironment = copy.deepcopy(environment)
			qualifiers = selector
			if "__qualifiers" in environment:
				qualifiers = combineLists(environment["__qualifiers"], qualifiers)
				
			subEnvironment["__qualifiers"] = qualifiers
			if not compile(context, sub, subEnvironment):
				return False
		
		elif type == 'Gamerule':
			if context["sections"][context["section"]]["type"] == "reset":
				print "'gamerule' block may not appear in a 'reset' section."
				return False
			
			id, op, rhs, sub = content
			
			context["gamerules"][id] = True
			context["sections"][context["section"]]["gamerules"][id] = True
			
			prefix = "/execute @p[GR{0}{1}{2}] ~ ~ ~ ".format(id, op, rhs)
			
			if not compileWithPrefix(context, sub, environment, prefix):
				return False

		elif type == 'Trigger':
			selector, objective, sub = content
	
			context["triggers"][objective] = True
			
			fullselector = combineSelectors(selector, "[{0}]".format(objective))
			prefix = "/execute {0} ~ ~ ~ ".format(fullselector)
			if not compileWithPrefix(context, sub, environment, prefix):
				return False
				
			addCommand(context, environment, "/scoreboard players set {0} {1} 0".format(selector, objective))
			addCommand(context, environment, "/scoreboard players enable {0} {1}".format(selector, objective))			
		
		elif type == 'As':
			selector, sub, relcoords, detect = content
			
			prefix = "/execute {0} {1}{2} ".format(selector, relcoords, detect)
			
			if not compileWithPrefix(context, sub, environment, prefix):
				return False
		
		elif type == 'If':
			command, yes, no = content
			
			addCommand(context, environment, command)

			sectionName = context["section"]
			section = context["sections"][sectionName]
			commands = section["commands"]

			ifStart = len(commands)
			
			if len(yes) > 0:
				yesFill = addConditionalCommand(context, environment, "/fill ~-1 ~ ~ZS ~-1 ~ ~ZE redstone_block")
			
			if len(no) > 0:
				noFill = addConditionalCommand(context, environment, "/fill ~-1 ~ ~ZS ~-1 ~ ~ZE stone")
			
			if len(yes) > 0:
				yesStart = len(commands)-1
				
				auto = context['auto']
				context['auto'] = DEFAULTOFF
				if not compile(context, yes, environment):
					return False
					
				yesEnd = len(commands)-1

				commands[yesFill] = commands[yesFill].replace("ZS", str(yesStart - yesFill + 1))
				commands[yesFill] = commands[yesFill].replace("ZE", str(yesEnd - yesFill + 1))

				# For the "yes" portion, only run the undo if the "yes" portion was run
				yesUndo = yesEnd + 1
				addCommand(context, environment, "/fill ~-1 ~ ~{0} ~-1 ~ ~{1} stone".format(yesStart - yesUndo + 1, yesEnd - yesUndo + 1))

				context['auto'] = auto
				

			if len(no) > 0:
				noStart = len(commands)-1
				
				auto = context['auto']
				context['auto'] = DEFAULTON
				if not compile(context, no, environment):
					return False
				context['auto'] = auto
					
				noEnd = len(commands)-1
				
				commands[noFill] = commands[noFill].replace("ZS", str(noStart - noFill + 1))
				commands[noFill] = commands[noFill].replace("ZE", str(noEnd - noFill))
				
				# For the "no" portion, run the undo even if the "no" portion was run
				noUndo = noEnd + 1
				addCommand(context, environment, "/fill ~-1 ~ ~{0} ~-1 ~ ~{1} redstone_block".format(noStart - noUndo + 1, noEnd - noUndo))
				
		elif type == 'Tell':
			selector, unformatted = content
			
			text = formatJsonText(unformatted, context, environment)
			command = '/tellraw {0} {1}'.format(selector, text)
			addCommand(context, environment, command)
				
		elif type == 'Assignment':
			id, python = content
			
			try:
				environment[id] = eval(python, globals(), environment)
			except:
				print "Could not evaluate: " + python
				return False
			
		elif type == 'SelectorAssignment':
			id, selector, qualifiers = content
			if "@"+selector in environment:
				if qualifiers:
					fullselector = environment["@"+selector][:-1] + "," + qualifiers + "]"
				else:
					fullselector = environment["@"+selector]
			else:
				fullselector = "@{0}[{1}]".format(selector, qualifiers)
				
			environment["@"+id] = applyEnvironment(fullselector, environment)

		elif type == 'Math':
			selector, objective, op, expr, match = content
			
			selector = applyEnvironment(selector, environment)
			registerObjective(context, objective)
			
			if op in ['AffectedBlocks', 'AffectedEntities', 'AffectedItems', 'QueryResult', 'SuccessCount']:
				selector, objective, stat, sub, _ = content
				addCommand(context, environment, "/scoreboard players set {0} {1} 0".format(selector, objective))
				addCommand(context, environment, "/stats entity {0} set {1} {3} {2}".format(selector, op, objective, combineSelectors(selector, "[c=1]")))
				prefix = "/execute {0} ~ ~ ~ ".format(selector)
				if not compileWithPrefix(context, sub, environment, prefix):
					return False
				addCommand(context, environment, "/stats entity {0} clear {1}".format(selector, op))
				
			elif op in ['+=', '-=', '=', '++', '--'] and expr[0] == 'NUM':
				operand = applyEnvironment(expr[1], environment)
				if not isNumber(operand):
					print "Unable to apply {0} to {1}.".format(op, operand)
					return False
				operand = int(operand)
			
				if op == '+=':
					opword = 'add'
				elif op == '-=':
					opword = 'remove'
				elif op == '=':
					opword = 'set'
				else:
					print "Unknown selector arithmetic operation: '{0}'".format(op)
					return False
					
				command = "/scoreboard players {0} {1} {2} {3}".format(opword, selector, objective, operand)
				if match:
					command = command + " " + match
				command = applyEnvironment(command, environment)
				
				qualifiers = ""
				if "__qualifiers" in environment:
					qualifiers = applyEnvironment(environment["__qualifiers"], environment)
				command = interpretSelectors(command, qualifiers, context)
				if command == None:
					print "Unable to apply qualifiers {0} and {1}".format(optqualifiers, qualifiers)
					return False
				
				addCommand(context, environment, command)
			elif expr[0] == 'NUM':
				operand = applyEnvironment(expr[1], environment)
				if not isNumber(operand):
					print "Unable to apply {0} to {1}.".format(op, operand)
					return False
				operand = int(operand)
			
				id2 = addConstant(context, operand)
				command = "/scoreboard players operation {0} {1} {2} {3} {4}".format(selector, objective, op, id2, "Constant")
				
				qualifiers = ""
				if "__qualifiers" in environment:
					qualifiers = applyEnvironment(environment["__qualifiers"], environment)
				command = interpretSelectors(command, qualifiers, context)
				if command == None:
					print "Unable to apply qualifiers {0} and {1}".format(optqualifiers, qualifiers)
					return False
				
				addCommand(context, environment, command)
			else:
				scratch = {"scratch": {}, "temp": {}}
				
				qualifiers = ""
				if "__qualifiers" in environment:
					qualifiers = applyEnvironment(environment["__qualifiers"], environment)
					
				output = calcMath(selector, expr, context, scratch, environment)
				if output == None:
					return False
				
				addOperation(context, environment, selector, objective, op, output)
				
				context["scratch"] = max(context["scratch"], len(scratch["scratch"].keys()))
				context["temp"] = max(context["temp"], len(scratch["temp"].keys()))
		elif type == 'Enable' or type == 'Disable':
			section = content
			if section not in context["sections"]:
				print "Cannot {0} section '{1}' because it doesn't exist.".format(type, section)
				return False
			
			if context["sections"][section]["type"] <> "clock":
				print "Can't enable or disable {0} sections.".format(context["sections"][section]["type"])
				return False
			
			(sx, sy, sz) = context["sections"][section]["pos"]
			(rx, ry, rz) = context["sections"]["reset"]["pos"]
			dx = sx - rx
			dy = sy - ry
			dz = sz - rz
			
			if type == 'Enable':
				addCommand(context, environment, "/execute @e[type=armor_stand,name={0}] ~{1} ~{2} ~{3} /setblock ~ ~ ~ redstone_block".format(context["name"], dx, dy, dz))
			else:
				addCommand(context, environment, "/execute @e[type=armor_stand,name={0}] ~{1} ~{2} ~{3} /setblock ~ ~ ~ stone".format(context["name"], dx, dy, dz))
		
		elif type == 'Call':
			function = content
			
			if function not in context["sections"]:
				print "Cannot call function '{0}' because it doesn't exist.".format(function)
				return False
			
			if context["sections"][function]["type"] <> "function":
				print "Can't call {0} sections.".format(context["sections"][function]["type"])
				return False
			
			addCommand(context, environment, "/execute @e[type=armor_stand,name={0}] ~ ~ ~ /fill #min{1}# #max{1}# redstone_block".format(context["name"], function))
			addCommand(context, environment, "/execute @e[type=armor_stand,name={0}] ~ ~ ~ /fill #min{1}# #max{1}# stone".format(context["name"], function))
		
		else:
			print "Unknown block type: " + type

	return True
			
def run():
	while True:
		updateScript()
		if script["applied"] == False:
			print "Applying " + os.path.basename(script["path"])
			success = False
			try:
				success = applyScript(script)
			except Exception as e:
				print "Compiler encountered unexpected error during compilation."
				print type(e)
				print e.args
				print e
				traceback.print_exc()
			if success:
				print "Script successfully applied."
			else:
				print "Script had compile error(s).\a"
			
			script["applied"] = True
		time.sleep(1)
	

run()