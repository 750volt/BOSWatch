#!/usr/bin/python
# -*- coding: cp1252 -*-

"""
MySQL-Plugin to dispatch FMS-, ZVEI- and POCSAG - messages to a MySQL database

@author: Jens Herrmann
@author: Bastian Schroll

@requires: MySQL-Configuration has to be set in the config.ini
@requires: Created Database/Tables, see boswatch.sql
"""

import logging # Global logger

import mysql
import mysql.connector

from includes import globals  # Global variables

##
#
# onLoad function of plugin
# will be called by the pluginLoader
#
def onLoad():
	"""
	While loading the plugins by pluginLoader.loadPlugins()
	this onLoad() routine are called

	@requires:  nothing
	
	@return:    nothing
	"""
	try:
		########## User onLoad CODE ##########
		
		########## User onLoad CODE ##########
		
	except:
		logging.error("unknown error")
		logging.debug("unknown error", exc_info=True)

##
#
# Main function of MySQL-plugin
# will be called by the alarmHandler
#
def run(typ,freq,data):
	"""
	This function is the implementation of the MySQL-Plugin.
	It will store the data to an MySQL database
	
	The configuration for the MySQL-Connection is set in the config.ini.
	For DB- and tablestructure see boswatch.sql

	@type    typ:  string (FMS|ZVEI|POC)
	@param   typ:  Typ of the dataset for sending to BosMon
	@type    data: map of data (structure see interface.txt)
	@param   data: Contains the parameter for dispatch to BosMon.
	@type    freq: string
	@keyword freq: frequency is not used in this plugin

	@requires: MySQL-Configuration has to be set in the config.ini
	@requires: Created Database/Tables, see boswatch.sql
	
	@return:    nothing
	"""
	try:
		#
		#ConfigParser
		#
		logging.debug("reading config file")
		try:
			for key,val in globals.config.items("MySQL"):
				logging.debug(" - %s = %s", key, val)
		except:
			logging.error("cannot read config file")
			logging.debug("cannot read config file", exc_info=True)
			# Without config, plugin couldn't work
			return
				
		try:
		    #
			# Connect to MySQL
			#
			logging.debug("connect to MySQL")
			connection = mysql.connector.connect(host = globals.config.get("MySQL","dbserver"), user = globals.config.get("MySQL","dbuser"), passwd = globals.config.get("MySQL","dbpassword"), db = globals.config.get("MySQL","database"))
			cursor = connection.cursor()
		except:
			logging.error("cannot connect to MySQL")
			logging.debug("cannot connect to MySQL", exc_info=True)
			# Without connection, plugin couldn't work
			return
			
		else:
			try:
				#
				# Create and execute SQL-statement
				#
				logging.debug("Insert %s", typ)
				
				if typ == "FMS":
					#data = {"fms":fms_id[0:8], "status":fms_status, "direction":fms_direction, "tsi":fms_tsi}
					cursor.execute("INSERT INTO "+globals.config.get("MySQL","tableFMS")+" (time,fms,status,direction,tsi) VALUES (NOW(),%s,%s,%s,%s)",(data["fms"],data["status"],data["direction"],data["tsi"]))
					
				elif typ == "ZVEI":
					#data = {"zvei":zvei_id}
					#Don't use %s here (bug in mysql-lib with one parameter)
					cursor.execute("INSERT INTO "+globals.config.get("MySQL","tableZVEI")+" (time,zvei) VALUES (NOW(),"+(data["zvei"])+")")
					
				elif typ == "POC":
					#data = {"ric":poc_id, "function":poc_sub, "msg":poc_text}
					cursor.execute("INSERT INTO "+globals.config.get("MySQL","tablePOC")+" (time,ric,funktion,text) VALUES (NOW(),%s,%s,%s)",(data["ric"],data["function"],data["msg"]))
					
				else:
					logging.warning("Invalid Typ: %s", typ)	
			except:
				logging.error("cannot Insert %s", typ)
				logging.debug("cannot Insert %s", typ, exc_info=True)
				return
					 
		finally:
			logging.debug("close MySQL")
			try: 
				cursor.close()
				connection.close() #Close connection in every case  
			except:
				pass
			
	except:
		logging.error("unknown error")
		logging.debug("unknown error", exc_info=True)