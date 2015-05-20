#!/usr/bin/python
# -*- coding: cp1252 -*-

import logging # Global logger
import globals # Global variables

import httplib #for the HTTP request
import urllib #for the HTTP request with parameters
import base64 #for the HTTP request with User/Password

def run(typ,freq,data):
	try:
		#ConfigParser
		logging.debug("reading config file")
		try:
			for key,val in globals.config.items("BOSWatch"):
				logging.debug(" - %s = %s", key, val)
		except:
			logging.exception("cannot read config file")

			
		if typ == "FMS":
			logging.warning("FMS not implemented")
		
		elif typ == "ZVEI":
			logging.warning("ZVEI not implemented")
		
		elif typ == "POC":
			logging.debug("Start POC to BosMon")
			try:
				#Defined data structure:
				#   data["ric"]
				#   data["function"]
				#   data["msg"]
				#BosMon-Telegramin expected "a-d" as RIC-sub/function
				data["function"] = data["function"].replace("1", "a").replace("2", "b").replace("3", "c").replace("4", "d")
				params = urllib.urlencode({'type':'pocsag', 'address':data["ric"], 'flags':'0', 'function':data["function"], 'message':data["msg"]})
				logging.debug(" - Params: %s", params)
				headers = {}
				headers['Content-type'] = "application/x-www-form-urlencoded"
				headers['Accept'] = "text/plain"
				if bosmon_user:
					headers['Authorization'] = "Basic {0}".format(base64.b64encode("{0}:{1}".format(globals.config.get("BosMon", "bosmon_user"), globals.config.get("BosMon", "bosmon_password"))))
				httprequest = httplib.HTTPConnection(globals.config.get("BosMon", "bosmon_server"), globals.config.get("BosMon", "bosmon_port"))
				httprequest.request("POST", "/telegramin/"+bosmon_channel+"/input.xml", params, headers)
				httpresponse = httprequest.getresponse()
				if str(httpresponse.status) == "200": #Check HTTP Response an print a Log or Error
					logging.debug("BosMon response: %s - %s", str(httpresponse.status), str(httpresponse.reason))
				else:
					logging.warning("BosMon response: %s - %s", str(httpresponse.status), str(httpresponse.reason))
			except:
				logging.error("POC to BosMon failed")
		else:
			logging.warning("undefined typ '%s'", typ)
	except:
		logging.exception("")