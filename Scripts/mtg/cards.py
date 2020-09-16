import json
import os

Cards = {}

for dirpath, dirnames, filenames in os.walk('cards'):
	for filename in filenames:
		with open(os.path.join(dirpath, filename)) as file:
			obj = json.load(file)
			Cards[obj["Name"]] = obj
	
CardNames = []
CardNumbers = {}
i = 0
for name in Cards:
	CardNames.append(name)
	CardNumbers[name] = i
	i += 1