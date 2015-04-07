#!/usr/bin/python
# -*- coding: cp1252 -*-

##### Info #####
# BOSWatch
# Autor: Bastian Schroll
# Python Script to Recive and Decode German BOS Information with rtl_fm and multimon-NG
# For more Information see the README.md
##### Info #####

import time
#import sys
import subprocess
#import os
import mysql
import mysql.connector
import httplib

import argparse #for parse the args
import ConfigParser #for parse the config file
import re #Regex


# Functions
def curtime(format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format)	

#Loglevel 
#[LOG] for the logfile
#[INFO] normal display
#[ERROR] errors
def log(msg, level="log"):
	log_entry = curtime("%H:%M:%S")+" ["+level.upper()+"]	"+msg

	if not level == "log" and not args.quiet or args.verbose:
		print log_entry
		
	bos_log = open("log_bos.txt", "a")
	bos_log.write(log_entry+"\n")
	bos_log.close()
	

try:

	try:
		bos_log = open("log_bos.txt", "w")
		rtl_log = open("log_rtl.txt", "w")
		mon_log = open("log_mon.txt", "w")
		bos_log.write("##### "+curtime()+" #####\n\n")
		rtl_log.write("##### "+curtime()+" #####\n\n")
		mon_log.write("##### "+curtime()+" #####\n\n")
		bos_log.close()
		rtl_log.close()
		mon_log.close()
	except:
		log("cannot clear logfiles","error")

	try:
		#With -h or --help you get the Args help
		#ArgsParser
		parser = argparse.ArgumentParser(prog="boswatch.py", description="BOSWatch is a Python Script to Recive and Decode German BOS Information with rtl_fm and multimon-NG", epilog="More Options you can find in the extern config.ini File in this Folder")
		#parser.add_argument("-c", "--channel", help="BOS Channel you want to listen")
		parser.add_argument("-f", "--freq", help="Frequency you want to listen", required=True)
		parser.add_argument("-d", "--device", help="Device you want to use (Check with rtl_test)", type=int, default=0)
		parser.add_argument("-e", "--error", help="Frequency-Error of your Device in PPM", type=int, default=0)
		parser.add_argument("-a", "--demod", help="Demodulation Functions", choices=['FMS', 'ZVEI', 'POC512', 'POC1200', 'POC2400'], required=True, nargs="+")
		parser.add_argument("-s", "--squelch", help="Level of Squelch", type=int, default=0)
		parser.add_argument("-v", "--verbose", help="Shows more Information", action="store_true")
		parser.add_argument("-q", "--quiet", help="Shows no Information. Only Logfiles", action="store_true")
		args = parser.parse_args()
	except:
		log("cannot parse Args","error")

	#Read Data from Args, Put it into working Variables
	freq = args.freq
	device = args.device
	error = args.error
	
	demodulation = ""
	if "FMS" in args.demod:
		demodulation += "-a FMSFSK "
	if "ZVEI" in args.demod:
		demodulation += "-a ZVEI2 "
	if "POC512" in args.demod:
		demodulation += "-a POCSAG512 "
	if "POC1200" in args.demod:
		demodulation += "-a POCSAG1200 "	
	if "POC2400" in args.demod:
		demodulation += "-a POCSAG2400 "
		
	squelch = args.squelch

	if not args.quiet: #only if not quiet mode
		print "     ____  ____  ______       __      __       __    " 
		print "    / __ )/ __ \/ ___/ |     / /___ _/ /______/ /_  b" 
		print "   / __  / / / /\__ \| | /| / / __ `/ __/ ___/ __ \ e" 
		print "  / /_/ / /_/ /___/ /| |/ |/ / /_/ / /_/ /__/ / / / t" 
		print " /_____/\____//____/ |__/|__/\__,_/\__/\___/_/ /_/  a" 
		print "            German BOS Information Script            " 
		print "                 by Bastian Schroll                  " 
		print "" 
	
		print "Frequency:	"+freq
		print "Device-ID:	"+str(device)
		print "Error in PPM:	"+str(error)
		print "Active Demods:	"+str(len(args.demod))
		if "FMS" in args.demod:
			print "- FMS"
		if "ZVEI" in args.demod:
			print "- ZVEI" 
		if "POC512" in args.demod:
			print "- POC512"
		if "POC1200" in args.demod:
			print "- POC1200"
		if "POC2400" in args.demod:
			print "- POC2400" 
		print "Squelch:	"+str(squelch)
		if args.verbose:
			print "Verbose Mode!" 
		print ""	
		
	#ConfigParser
	log("reading config file")
	try:
		config = ConfigParser.ConfigParser()
		config.read("./config.ini")
		fms_double_ignore_time = int(config.get("FMS", "double_ignore_time"))
		zvei_double_ignore_time = int(config.get("ZVEI", "double_ignore_time"))
			
		#MySQL config
		useMySQL = int(config.get("Module", "useMySQL")) #use MySQL support?
		if useMySQL: #only if MySQL is active
			dbserver = config.get("MySQL", "dbserver")
			dbuser = config.get("MySQL", "dbuser")
			dbpassword = config.get("MySQL", "dbpassword")
			database = config.get("MySQL", "database")
				
			#MySQL tables
			tableFMS = config.get("MySQL", "tableFMS")
			tableZVEI = config.get("MySQL", "tableZVEI")
			tablePOC = config.get("MySQL", "tablePOC") 
				
		#HTTPrequest config
		useHTTPrequest = int(config.get("Module", "useHTTPrequest")) #use HTTPrequest support?
		if useHTTPrequest: #only if HTTPrequest is active
			url = config.get("HTTPrequest", "url")
			
	except:
		log("cannot read config file","error")
			
	#variables pre-load
	log("pre-load variables")
	fms_id = 0
	fms_id_old = 0
	fms_time_old = 0
		
	zvei_id = 0
	zvei_id_old = 0
	zvei_time_old = 0
	
	if useMySQL: #only if MySQL is active
		log("connect to MySQL database")
		try:
			connection = mysql.connector.connect(host = str(dbserver), user = str(dbuser), passwd = str(dbpassword), db = str(database))
		except:
			log("cannot connect to MySQL database","error")
			
			
	log("starting rtl_fm")
	try:
		rtl_fm = subprocess.Popen("rtl_fm -d "+str(device)+" -f "+str(freq)+" -M fm -s 22050 -p "+str(error)+" -E DC -F 0 -l "+str(squelch)+" -g 100",
									#stdin=rtl_fm.stdout,
									stdout=subprocess.PIPE,
									stderr=open('log_rtl.txt','a'),
									shell=True)
	except:
		log("cannot start rtl_fm","error")
		
	#multimon_ng = subprocess.Popen("aplay -r 22050 -f S16_LE -t raw",
	log("starting multimon-ng")
	try:
		multimon_ng = subprocess.Popen("multimon-ng "+str(demodulation)+" -f alpha -t raw /dev/stdin - ",
									stdin=rtl_fm.stdout,
									stdout=subprocess.PIPE,
									stderr=open('log_mon.txt','a'),
									shell=True)
	except:
		log("cannot start multimon-ng","error")
			
			
	log("start decoding")	
	while True:	
		#RAW Data from Multimon-NG
		#ZVEI2: 25832
		#FMS: 43f314170000 (9=Rotkreuz      3=Bayern 1        Ort 0x25=037FZG 7141Status 3=Einsatz Ab    0=FZG->LST2=III(mit NA,ohneSIGNAL)) CRC correct\n'	
		decoded = str(multimon_ng.stdout.readline()) #Get line data from multimon stdout
			
		if True: #if input data avalable
			
			timestamp = int(time.time())#Get Timestamp					
			#if args.verbose: print "RAW: "+decoded #for verbose mode, print Raw input data
				
			#FMS Decoder Section	
			#check FMS: -> check CRC -> validate -> check double alarm -> log -> (MySQL)
			if "FMS:" in decoded:	
				log("recived FMS")
					
				fms_service = decoded[19]		#Organisation
				fms_country = decoded[36] 		#Bundesland
				fms_location = decoded[65:67]	#Ort
				fms_vehicle = decoded[72:76]	#Fahrzeug
				fms_status = decoded[84]		#Status
				fms_direction = decoded[101]	#Richtung
				fms_tsi = decoded[114:117]		#Taktische Kruzinformation
					
				if "CRC correct" in decoded: #check CRC is correct	
					fms_id = fms_service+fms_country+fms_location+fms_vehicle+fms_status+fms_direction #build FMS id
					if re.search("[0-9a-f]{2}[0-9]{6}[0-9a-f]{1}[01]{1}", fms_id): #if FMS is valid
						if fms_id == fms_id_old and timestamp < fms_time_old + fms_double_ignore_time: #check for double alarm
							log("FMS double alarm: "+fms_id_old)
							fms_time_old = timestamp #in case of double alarm, fms_double_ignore_time set new
						else:
							log("BOS:"+fms_service+" Bundesland:"+fms_country+" Ort:"+fms_location+" Fahrzeug:"+fms_vehicle+" Status:"+fms_status+" Richtung:"+fms_direction+" TKI:"+fms_tsi,"info")
							fms_id_old = fms_id #save last id
							fms_time_old = timestamp #save last time	
							
							if useMySQL: #only if MySQL is active
								log("insert FMS into MySQL")
								try:
									cursor = connection.cursor()
									cursor.execute("INSERT INTO "+tableFMS+" (time,service,country,location,vehicle,status,direction,tsi) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(curtime(),fms_service,fms_country,fms_location,fms_vehicle,fms_status,fms_direction,fms_tsi))
									cursor.close()
									connection.commit()
								except:
									log("FMS cannot insert into MySQL","error")
									
									
							if useHTTPrequest: #only if HTTPrequest is active		
								log("FMS to HTTP request")
								try:
									httprequest = httplib.HTTPConnection(url)
									httprequest.request("HEAD", "/")
									httpresponse = httprequest.getresponse()
									#if args.verbose: print httpresponse.status, httpresponse.reason
								except:
									log("FMS HTTP request failed","error")
									
					else:
						log("No valid FMS: "+fms_id)	
				else:
					log("FMS CRC incorrect")
						
						
			#ZVEI Decoder Section
			#check ZVEI: -> validate -> check double alarm -> log -> (MySQL)	 
			if "ZVEI2:" in decoded:
				log("recived ZVEI")
					
				zvei_id = decoded[7:12]	#ZVEI Code	
				if re.search("[0-9F]{5}", zvei_id): #if ZVEI is valid
					if zvei_id == zvei_id_old and timestamp < zvei_time_old + zvei_double_ignore_time: #check for double alarm
						log("ZVEI double alarm: "+zvei_id_old)
						zvei_time_old = timestamp #in case of double alarm, zvei_double_ignore_time set new
					else:
						log("5-Ton: "+zvei_id,"info")
						zvei_id_old = zvei_id #save last id
						zvei_time_old = timestamp #save last time
							
							
						if useMySQL: #only if MySQL is active
							log("insert ZVEI into MySQL")
							try:
								cursor = connection.cursor()
								cursor.execute("INSERT INTO "+tableZVEI+" (time,zvei) VALUES (%s,%s)",(curtime(),zvei_id))
								cursor.close()
								connection.commit()
							except:
								log("ZVEI cannot insert into MySQL","error")
						
							
						if useHTTPrequest: #only if HTTPrequest is active
							log("ZVEI to HTTP request")	
							try:
								httprequest = httplib.HTTPConnection(url)
								httprequest.request("HEAD", "/")
								httpresponse = httprequest.getresponse()
								#if args.verbose: print httpresponse.status, httpresponse.reason
							except:
								log("ZVEI HTTP request failed","error")
								
				else:
					log("No valid ZVEI: "+zvei_id)
						
except KeyboardInterrupt:
	log("Keyboard Interrupt","error")
except:
	log("unknown Error","error")
finally:
	if useMySQL: #only if MySQL is active
		log("disconnect MySQL") 
		connection.close()
	rtl_fm.terminate()
	log("rtl_fm terminated") 
	multimon_ng.terminate()
	log("multimon-ng terminated")
	log("exiting BOSWatch")		
	exit(0)