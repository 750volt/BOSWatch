#!/usr/bin/python
# -*- coding: cp1252 -*-

"""
Functions for the RegEX Filter

@author: Bastian Schroll

@requires: Configuration has to be set in the config.ini
"""

import logging # Global logger

import re #Regex for Filter Check

from includes import globals  # Global variables


def loadFilters():
	"""
	load all Filters from the config.ini into globals.filterList

	@requires:  Configuration has to be set in the config.ini
	
	@return:    nothing
	@exception: Exception if Filter loading failed
	"""
	try:
		logging.debug("loading filters")
		#For each entry in config.ini [Filters] Section
		for key,val in globals.config.items("Filters"):
			logging.debug(" - %s = %s", key, val)
			filter = val.split(";")
			#insert splitet Data into globals.filterList
			globals.filterList.append({"name": key, "typ": filter[0], "dataField": filter[1], "plugin": filter[2], "regex": filter[3]})
	except:
		logging.exception("cannot read config file")
	
	
def checkFilters(data,typ,plugin):
	"""
	Check the Typ/Plugin combination with the RegEX Filter
	If no Filter for the combination is found, Function returns True.

	@type    data: map of data (structure see interface.txt)
	@param   data: Contains the parameter
	@type    typ:  string (FMS|ZVEI|POC)
	@param   typ:  Typ of the dataset
	@type    plugin: string
	@param   plugin: Name of the Plugin to checked
	
	@requires:  all Filters in the filterList
	
	@return:    nothing
	@exception: Exception if Filter check failed
	"""
	try:
		logging.debug("search Filter for %s to %s", typ, plugin)
		
		foundFilter = False
		#go to all Filter in globals.filterList
		for i in globals.filterList:
			#if Typ/Plugin combination is found
			if i["typ"] == typ and i["plugin"] == plugin:
				foundFilter = True
				logging.debug("found Filter: %s = %s", i["name"], i["regex"])
				#Check the RegEX
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