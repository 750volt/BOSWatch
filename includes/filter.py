#!/usr/bin/python
# -*- coding: cp1252 -*-

import logging # Global logger

import re #Regex for Filter Check

from includes import globals  # Global variables


def loadFilters():
	try:
		logging.debug("loading filters")
		for key,val in globals.config.items("Filters"):
			logging.debug(" - %s = %s", key, val)
			filter = val.split(";")
			globals.filterList.append({"name": key, "typ": filter[0], "dataField": filter[1], "plugin": filter[2], "regex": filter[3]})
	except:
		logging.exception("cannot read config file")
	
	
def checkFilters(data,typ,plugin):
	try:
		logging.debug("search Filter for %s to %s", typ, plugin)
		
		foundFilter = False
		for i in globals.filterList:
			if i["typ"] == typ and i["plugin"] == plugin:
				foundFilter = True
				logging.debug("found Filter: %s = %s", i["name"], i["regex"])
				if re.search(i["regex"], data[i["dataField"]]):
					logging.debug("Filter passed: %s", i["name"])
					return True
				else:
					logging.debug("Filter not passed: %s", i["name"])
			
		if foundFilter:
			logging.debug("no Filter passed")
			return False
		else:
			logging.debug("no Filter found")
			return True
			
	except:
		logging.exception("Error in Filter checking")