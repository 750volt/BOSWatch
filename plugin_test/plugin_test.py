#!/usr/bin/python
# -*- coding: cp1252 -*-

import globals  # Global variables
import time
import pluginloader

import os #for absolute path: os.path.dirname(os.path.abspath(__file__))
import ConfigParser #for parse the config file

import logging

#create new logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#set log string format
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', '%d.%m.%Y %I:%M:%S')

#create a file loger
fh = logging.FileHandler('boswatch.log', 'w')
fh.setLevel(logging.DEBUG) #log level >= Debug
fh.setFormatter(formatter)
logger.addHandler(fh)

#create a display loger
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR) #log level >= Error
ch.setFormatter(formatter)
logger.addHandler(ch)

#https://docs.python.org/2/howto/logging.html#logging-basic-tutorial
#log levels
#----------
#debug - debug messages only for log
#info - inormation for normal display
#warning
#error - normal error - program goes further
#exception - error with exception message in log
#critical - critical error, program exit

#ConfigParser
try:
	logging.debug("reading config file")
	script_path = os.path.dirname(os.path.abspath(__file__))
	globals.config = ConfigParser.ConfigParser()
	globals.config.read(script_path+"/config/config.ini")
except:
	logging.exception("cannot read config file")

#data = {"zvei":"12345"}
data = {"ric":"1234567", "function":"1", "msg":"Hello World!"}

while True:
    time.sleep(1)
    logging.info("Alarm!")
    for i in pluginloader.getPlugins():
        logging.debug("Load Plugin: " + i["name"])
        plugin = pluginloader.loadPlugin(i)
        plugin.run("POC","80000000",data)