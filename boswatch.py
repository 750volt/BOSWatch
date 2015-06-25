#!/usr/bin/python
# -*- coding: cp1252 -*-
#
"""
BOSWatch
Python script to receive and decode German BOS information with rtl_fm and multimon-NG
Through a simple plugin system, data can easily be transferred to other applications
For more information see the README.md

@author: 		Bastian Schroll
@author: 		Jens Herrmann

GitHUB:		https://github.com/Schrolli91/BOSWatch
"""

import logging
import logging.handlers

import argparse     # for parse the args
import ConfigParser # for parse the config file
import os           # for log mkdir
import time         # for timestamp
import subprocess   # for starting rtl_fm and multimon-ng

from includes import globals  # Global variables
from includes import MyTimedRotatingFileHandler  # extension of TimedRotatingFileHandler 
from includes import converter  # converter functions
from includes import signalHandler  # TERM-Handler for use script as a daemon
		

#
# ArgParser
# Have to be before main program
#
try:	
	# With -h or --help you get the Args help
	parser = argparse.ArgumentParser(prog="boswatch.py", 
									description="BOSWatch is a Python Script to recive and decode german BOS information with rtl_fm and multimon-NG", 
									epilog="More options you can find in the extern config.ini file in the folder /config")
	# parser.add_argument("-c", "--channel", help="BOS Channel you want to listen")
	parser.add_argument("-f", "--freq", help="Frequency you want to listen", required=True)
	parser.add_argument("-d", "--device", help="Device you want to use (Check with rtl_test)", type=int, default=0)
	parser.add_argument("-e", "--error", help="Frequency-Error of your device in PPM", type=int, default=0)
	parser.add_argument("-a", "--demod", help="Demodulation functions", choices=['FMS', 'ZVEI', 'POC512', 'POC1200', 'POC2400'], required=True, nargs="+")
	parser.add_argument("-s", "--squelch", help="Level of squelch", type=int, default=0)
	parser.add_argument("-u", "--usevarlog", help="Use '/var/log/boswatch' for logfiles instead of subdir 'log' in BOSWatch directory", action="store_true")
	parser.add_argument("-v", "--verbose", help="Shows more information", action="store_true")
	parser.add_argument("-q", "--quiet", help="Shows no information. Only logfiles", action="store_true")
	args = parser.parse_args()	
except SystemExit:
	# -h or --help called, exit right now
	exit(0)
except:
	print "cannot parsing the arguments"

	
#
# Main program
#
try:
	# initialization
	try:
		#
		# Script-pathes
		#
		globals.script_path = os.path.dirname(os.path.abspath(__file__))

		#
		# Set log_path
		#
		if args.usevarlog:
			globals.log_path = "/var/log/BOSWatch/"
		else:
			globals.log_path = globals.script_path+"/log/"

		#
		# If necessary create log-path
		#
		if not os.path.exists(globals.log_path):
			os.mkdir(globals.log_path)
			
		#
		# Create new myLogger...
		#
		myLogger = logging.getLogger()
		myLogger.setLevel(logging.DEBUG)
		# set log string format
		formatter = logging.Formatter('%(asctime)s - %(module)-15s [%(levelname)-8s] %(message)s', '%d.%m.%Y %H:%M:%S')
		# create a file logger
		fh = MyTimedRotatingFileHandler.MyTimedRotatingFileHandler(globals.log_path+"boswatch.log", "midnight", interval=1, backupCount=999)
		# Starts with log level >= Debug
		# will be changed with config.ini-param later
		fh.setLevel(logging.DEBUG) 
		fh.setFormatter(formatter)
		myLogger.addHandler(fh)
		# create a display logger
		ch = logging.StreamHandler()
		# log level for display >= info
		# will be changed later after parsing args
		ch.setLevel(logging.INFO) 
		ch.setFormatter(formatter)
		myLogger.addHandler(ch)		
	except:
		logging.exception("cannot create logger")
	else:	
	# initialization of the logging was fine, continue...
		
		try:
			#
			# Clear the logfiles
			#
			fh.doRollover()
			rtl_log = open(globals.log_path+"rtl_fm.log", "w")
			mon_log = open(globals.log_path+"multimon.log", "w")
			rtl_log.write("")
			mon_log.write("")
			rtl_log.close()
			mon_log.close()
			logging.debug("BOSWatch has started")
			logging.debug("Logfiles cleared")		
		except:
			logging.exception("cannot clear Logfiles")	
			
		try:	
			#
			# For debug display/log args
			#
			logging.debug(" - Frequency: %s", converter.freqToHz(args.freq))
			logging.debug(" - Device: %s", args.device)
			logging.debug(" - PPM Error: %s", args.error)
			logging.debug(" - Squelch: %s", args.squelch)
			
			demodulation = ""
			if "FMS" in args.demod:
				demodulation += "-a FMSFSK "
				logging.debug(" - Demod: FMS")
			if "ZVEI" in args.demod:
				demodulation += "-a ZVEI2 "
				logging.debug(" - Demod: ZVEI")
			if "POC512" in args.demod:
				demodulation += "-a POCSAG512 "
				logging.debug(" - Demod: POC512")
			if "POC1200" in args.demod:
				demodulation += "-a POCSAG1200 "
				logging.debug(" - Demod: POC1200")		
			if "POC2400" in args.demod:
				demodulation += "-a POCSAG2400 "
				logging.debug(" - Demod: POC2400")
			
			logging.debug(" - Use /var/log: %s", args.usevarlog)
			logging.debug(" - Verbose Mode: %s", args.verbose)
			logging.debug(" - Quiet Mode: %s", args.quiet)

			if args.verbose:
				ch.setLevel(logging.DEBUG)	
			if args.quiet:
				ch.setLevel(logging.CRITICAL)
			
			if not args.quiet: #only if not quiet mode
				from includes import shellHeader
				shellHeader.printHeader(args)					
		except:
			logging.exception("cannot display/log args")		

		try:
			#
			# Read config.ini
			#
			logging.debug("reading config file")
			globals.config = ConfigParser.ConfigParser()
			globals.config.read(globals.script_path+"/config/config.ini")
			# if given loglevel is debug:
			if globals.config.getint("BOSWatch","loglevel") == 10: 
				logging.debug(" - BOSWatch:")
				for key,val in globals.config.items("BOSWatch"):
					logging.debug(" -- %s = %s", key, val)
				logging.debug(" - FMS:")
				for key,val in globals.config.items("FMS"):
					logging.debug(" -- %s = %s", key, val)
				logging.debug(" - ZVEI:")
				for key,val in globals.config.items("ZVEI"):
					logging.debug(" -- %s = %s", key, val)
				logging.debug(" - POC:")
				for key,val in globals.config.items("POC"):
					logging.debug(" -- %s = %s", key, val)
		except:
			logging.exception("cannot read config file")
		else:
		# initialization was fine, continue with main program...
			
			try:
				# 
				# Set the loglevel and backupCount of the file handler 
				#
				logging.debug("set loglevel of fileHandler to: %s",globals.config.getint("BOSWatch","loglevel"))
				fh.setLevel(globals.config.getint("BOSWatch","loglevel"))
				logging.debug("set backupCount of fileHandler to: %s", globals.config.getint("BOSWatch","backupCount"))
				fh.setBackupCount(globals.config.getint("BOSWatch","backupCount"))
			except:
				logging.exception("cannot set loglevel of fileHandler")
			
			#
			# Load plugins
			#
			from includes import pluginLoader
			pluginLoader.loadPlugins()
			
			#
			# Load filters
			#
			if globals.config.getint("BOSWatch","useRegExFilter"):
				from includes import filter
				filter.loadFilters()
			
			#
			# Load description lists
			#
			if globals.config.getint("BOSWatch","useDescription"):
				from includes import descriptionList
				descriptionList.loadDescriptionLists()
			
			try:				
				#
				# Start rtl_fm
				#
				logging.debug("starting rtl_fm")
				command = "/usr/local/bin/rtl_fm -d "+str(args.device)+" -f "+str(converter.freqToHz(args.freq))+" -M fm -s 22050 -p "+str(args.error)+" -E DC -F 0 -l "+str(args.squelch)+" -g 100"
				rtl_fm = subprocess.Popen(command.split(),
						#stdin=rtl_fm.stdout,
						stdout=subprocess.PIPE,
						stderr=open(globals.log_path+"rtl_fm.log","a"),
						shell=False)
			except:
				logging.exception("cannot start rtl_fm")
			else:	
			# rtl_fm started, continue...
				
				try:
					#
					# Start multimon
					#
					logging.debug("starting multimon-ng")
					command = "/usr/local/bin/multimon-ng "+str(demodulation)+" -f alpha -t raw /dev/stdin - "
					multimon_ng = subprocess.Popen(command.split(),
						stdin=rtl_fm.stdout,
						stdout=subprocess.PIPE,
						stderr=open(globals.log_path+"multimon.log","a"),
						shell=False)						
				except:
					logging.exception("cannot start multimon-ng")
				else:				
				# multimon-ng started, continue...
					
					logging.debug("start decoding")  
					
					while True: 
						#
						# Get decoded data from multimon-ng and call BOSWatch-decoder
						#
					
						# RAW Data from Multimon-NG
						# ZVEI2: 25832
						# FMS: 43f314170000 (9=Rotkreuz      3=Bayern 1        Ort 0x25=037FZG 7141Status 3=Einsatz Ab    0=FZG->LST2=III(mit NA,ohneSIGNAL)) CRC correct\n' 
						# POCSAG1200: Address: 1234567  Function: 1  Alpha:   Hello World
						decoded = str(multimon_ng.stdout.readline()) #Get line data from multimon stdout
						
						# Test-strings only for develop
						#decoded = "ZVEI2: 25832"
						#decoded = "FMS: 43f314170000 (9=Rotkreuz       3=Bayern 1         Ort 0x25=037FZG  7141Status  3=Einsatz Ab     0=FZG->LST 2=I  (ohneNA,ohneSIGNAL)) CRC correct\n'"
						#decoded = "FMS: 43f314170000 (9=Rotkreuz       3=Bayern 1         Ort 0x25=037FZG  7141Status  3=Einsatz Ab     1=LST->FZG 2=I  (ohneNA,ohneSIGNAL)) CRC correct\n'"
						#decoded = "FMS: 43f314170000 (9=Rotkreuz       3=Bayern 1         Ort 0x25=037FZG  7141Status  3=Einsatz Ab     0=FZG->LST 2=II (ohneNA,mit SIGNAL)) CRC correct\n'"
						#decoded = "FMS: 43f314170000 (9=Rotkreuz       3=Bayern 1         Ort 0x25=037FZG  7141Status  3=Einsatz Ab     1=LST->FZG 2=III(mit NA,ohneSIGNAL)) CRC correct\n'"
						#decoded = "FMS: 43f314170000 (9=Rotkreuz       3=Bayern 1         Ort 0x25=037FZG  7141Status  3=Einsatz Ab     0=FZG->LST 2=IV (mit NA,mit SIGNAL)) CRC correct\n'"
						#decoded = "POCSAG1200: Address: 1234567  Function: 1  Alpha:   Hello World"
						#time.sleep(1)	
						
						from includes import decoder
						decoder.decode(converter.freqToHz(args.freq), decoded)
								
except KeyboardInterrupt:
	logging.warning("Keyboard Interrupt")	
except SystemExit:
	# SystemExitException is thrown if daemon was terminated
	logging.warning("SystemExit received")
	# only exit to call finally-block
	exit(0)
except:
	logging.exception("unknown error")
finally:
	try:
		logging.debug("BOSWatch shuting down")
		logging.debug("terminate multimon-ng (%s)", multimon_ng.pid) 
		multimon_ng.terminate()
		multimon_ng.wait()
		logging.debug("multimon-ng terminated")
		logging.debug("terminate rtl_fm (%s)", rtl_fm.pid) 
		rtl_fm.terminate()
		rtl_fm.wait()
		logging.debug("rtl_fm terminated") 
		logging.debug("exiting BOSWatch")		
	except:
		logging.warning("failed in clean-up routine")	
		
	finally:	
		# Close Logging
		logging.debug("close Logging")	
		logging.info("BOSWatch exit()")
		logging.shutdown()
		fh.close()
		ch.close()
		exit(0)