#!/usr/bin/python
# -*- coding: cp1252 -*-

import logging # Global logger
import globals # Global variables

def run(typ,freq,data):
	try:
		#ConfigParser
		#config Data in config["OPTION"]
		logging.debug("reading config file")
		try:
			config = dict(globals.config.items("template"))
			for key,val in config.items():
				logging.debug(" - %s = %s", key, val)
		except:
			logging.exception("cannot read config file")
	
		if typ == "FMS":
			logging.debug("FMS: %s Status: %s Dir: %s TKI: %s", data["fms"], data["status"], data["direction"], data["tki"])
		elif typ == "ZVEI":
			logging.debug("ZVEI: %s", data["zvei"])
		elif typ == "POC":
			logging.debug("POC: %s-%s - %s", data["ric"], data["function"], data["msg"])
		else:
			logging.warning(typ + " not supportet")
			
	except:
		logging.exception("unknown error")