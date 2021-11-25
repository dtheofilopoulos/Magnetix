#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path, subprocess, time, feedparser
from urllib.request import Request, urlopen

os.system("clear")

###  FORMATTED TERMINAL OUTPUT  ###################################################################
AEC = {
	"BLD":"\33[01m", "UND":"\33[04m",
	"RED":"\33[91m", "GRN":"\33[92m", "YLW":"\33[93m", "BLU":"\33[94m", "CYN":"\33[36m",
	"RSC":"\33[39m", "RST":"\33[00m",
	"PASS":"[+]", "WARN":"[-]", "ERROR":"[x]",
}

###  CREDITS  #####################################################################################
PRONAME = os.path.basename(__file__)
VERSION = "v2.4"

print((
 """{BLD}""" + PRONAME + """, """ + VERSION + """{RST} | EZTV Torrent Downloader

	Downloads matching TV Series titles as soon as they air on eztv and
	automatically queues the torrents to a running transmission daemon

	License  | Dio ( classicrocker384@gmail.com ), {UND}3-Clause BSD License{RST}
	Revision | 25/11/2021, 19:46
	Depends  | python, transmission-remote
	
 ------------------------------------------------------------------------------
 """).format(**AEC))

###  CONFIGURATION  ###############################################################################
DIRECTORY = os.path.dirname(__file__) + "/pyEZTV/"	# Absolute PATH of working directory
WATCHLIST = DIRECTORY + "series.db"			# TV SERIES watchlist
HASHESLOG = DIRECTORY + "torrent.log"			# History log of matched torrents w/ hashes
TORRENTDB = DIRECTORY + "torrent.db"			# Matched torrents database w/ magnet links

###  SETTINGS  ####################################################################################
RSSXMLURI = "https://eztv.re/ezrss.xml"			# RSS2.0 XML URI
TOR_WRITE = "ON"					# Keep magnet URIs in Torrent DB   [ON|OFF]
LOG_WRITE = "ON"					# Keep torrents in history log     [ON|OFF]
DAYS2KEEP = "1"						# Clean history log after x days
FILTER_TR = "ON"					# Activate filter (need BLACKLIST) [ON|OFF]
BLACKLIST = ["x265",".avi$",]				# Do NOT download FILENAMES w/ these tags

###  TRANSMISSION DAEMON  #########################################################################
ADDMAGNET = "ON"					# Add magnet URIs to transmission  [ON|OFF]
TRAN_HOST = "192.168.2.100"				# Transmission Daemon Host
TRAN_PORT = "9091"					# Transmission Daemon Port
USERNAME  = "transmission"				# Transmission Daemon Username
PASSWORD  = "yourpasswordgoeshere"			# Transmission Daemon Password

###  DEFINE VARIABLES  ############################################################################
TVSERIESDB = []
TORRENT_DB = []
HISTORYLOG = []
FILTER_SPC = []
TORRENTSDT = {}

###  Create data directory for the script if it does not exist
if (not os.path.exists(DIRECTORY)):
	os.makedirs(DIRECTORY)

###  Print the WATCHLIST
print((u" :::  {BLD}TV SERIES WATCHLIST{RST}  ::::::::::::::::::::::::::::::::::::::::::::::::::::").format(**AEC))
print(u"")
try:
	with open(WATCHLIST, "r") as TVSERIES:
		###  Alphabetical listing of watchlist
		TVSERIESDB = sorted(TVSERIES.read().strip().splitlines())
		
		if len(TVSERIESDB):
			i = 1
			for TVSERIESTITLES in TVSERIESDB:
				print(u"      " + str(i).zfill(2) + ". " + TVSERIESTITLES)
				i += 1
		else:
			print((u"     {BLD}{YLW} {WARN} {RST}" + WATCHLIST + " is {BLD}{YLW}EMPTY{RST}").format(**AEC))
			print((u"     {BLD}{YLW} {WARN} ADD{RST} TV series titles, separated by a new line (e.g. Family Guy)").format(**AEC))
			quit(u"")
		
except IOError:
	print((u"     {BLD}{RED} {ERROR} {RST}" + WATCHLIST + " {BLD}{RED}NOT ACCESSIBLE{RST}").format(**AEC))
	open(WATCHLIST, "w").close()
	print((u"     {BLD}{RED} {ERROR} {RST}" + WATCHLIST + " was {BLD}{GRN}CREATED{RST}").format(**AEC))
	quit(u"\n")
print(u"")


print((u"\n :::  {BLD}TV SERIES MATCHES{RST}  ::::::::::::::::::::::::::::::::::::::::::::::::::::::\n").format(**AEC))
###  if HASHESLOG has not been modified for more than x days, start CLEAN
if (LOG_WRITE == "ON"):
	try:
		CUR_TIME = time.time()
		MOD_TIME = os.path.getmtime(HASHESLOG)
		
		if (CUR_TIME - MOD_TIME >= int(DAYS2KEEP) * 24 * 3600):
			open(HASHESLOG, "w").close()
			print((u"     {BLD}{YLW} {WARN} {RST}" + HASHESLOG + " was {BLD}{YLW}TRUNCATED{RST}").format(**AEC))
		
	except:
		print((u"     {BLD}{RED} {ERROR} {RST}" + HASHESLOG + " was {BLD}{RED}NOT ACCESSIBLE{RST}").format(**AEC))
		open(HASHESLOG, "w").close()
		print((u"     {BLD}{RED} {ERROR} {RST}" + HASHESLOG + " was {BLD}{GRN}CREATED{RST}\n").format(**AEC))


###  Check the EZTV RSS2.0 URI and parse the XML
try:
	REQ = Request(RSSXMLURI, headers={'User-Agent': 'Mozilla/5.0'})
	XML = urlopen(REQ,timeout=10).read()
	
	###  Parse the XML for a limit of 50 entries
	XML_PARSED = feedparser.parse(XML).entries[:50]
	
except:
	print((u"     {BLD}{RED} {ERROR} {RSC}HTTP STATUS {RED}504{RSC}: GATEWAY TIMEOUT{RST} for URI " + RSSXMLURI).format(**AEC))


try:
	for XMLENTRY in XML_PARSED:
		
		###  FETCH RSS VARIABLES
		XMLTITLE = XMLENTRY.title
		XML_FILE = XMLENTRY.torrent_filename
		XML_HASH = XMLENTRY.torrent_infohash
		XML_MAGN = XMLENTRY.torrent_magneturi
		
		for SERIES in TVSERIESDB:
			
			###  make EZTV SERIES TITLES lowercase for easier regex
			if (SERIES.lower() in XMLTITLE.lower()):
				
				###  DO NOT download FILTERED names
				if (FILTER_TR == "ON"):
					
					if (any(FILTER in XML_FILE.lower() for FILTER in BLACKLIST)):
						FILTER_SPC = "1"
						print((u"     {BLD}{CYN} {WARN} FILTERED{RST} | " + XML_FILE).format(**AEC))[:95]
						continue
				
				###  in the off-chance that NO MAGNET URI in the XML, filter out the problematic torrent
				if (XML_MAGN == ""):
					print((u"     {BLD}{RED} {ERROR} NOMAGNET{RST} | " + XML_FILE).format(**AEC))[:94]
					continue
				
				###  Load historical hashes
				with open(HASHESLOG, "r") as HISTORY:
					for HASH in HISTORY:
						HASH = HASH.strip()
						if len(HASH):
							HISTORYLOG.append(HASH)
				
				###  Check the HISTORY LOG for already downloaded torrents
				if (XML_HASH in HISTORYLOG):
					FILTER_SPC = "1"
					print((u"     {BLD}{YLW} {WARN} EXISTING{RST} | " + XML_FILE).format(**AEC))[:95]
					continue
				else:
					HISTORYLOG.append(XML_HASH)
				
				###  Check for existing MAGNET LINKS
				if (XML_MAGN in TORRENT_DB):
					continue
				else:
					TORRENT_DB.append(XML_MAGN)
				
				###  Build the array with UNIQUE torrent matches based on infohash
				TORRENTSDT[XML_HASH] = { "TITLE": XMLTITLE, }
	
	
	###  WRITE LOGS FOR MATCHED TORRENTS
	LOGRESULTS = []
	for TOR in TORRENTSDT:
		### Write the TORRENT LOG. Append MAGNET URIs for MATCHED TORRENTS
		if (TOR_WRITE == "ON"):
			try:
				with open(TORRENTDB, "w") as MAGNETDB:
					for MAGNETURI in TORRENT_DB:
						MAGNETDB.write(MAGNETURI + "\n")
			
			except IOError:
				print((u"     {BLD}{RED} {ERROR} {RST}" + TORRENTDB + " was {BLD}{RED}NOT ACCESSIBLE{RST}").format(**AEC))
				
			
		### Write the HISTORY LOG. We DO NOT WANT to DOWNLOAD torrents twice
		if (LOG_WRITE == "ON"):
			try:
				with open(HASHESLOG, "w") as LOGDB:
					for HASH in HISTORYLOG:
						LOGDB.write(HASH + "\n")
			
			except IOError:
				print((u"     {BLD}{RED} {ERROR} {RST}" + HASHESLOG + " was {BLD}{RED}NOT ACCESSIBLE{RST}").format(**AEC))
				
		###  TITLES of TORRENT DOWNLOADS
		LOGRESULTS.append(TORRENTSDT[TOR]["TITLE"])
		

	###  PRINT TV SERIES MATCHES
	if (FILTER_TR == "ON" and FILTER_SPC == "1"):
		print(u"")
	
	if LOGRESULTS:
		print((u"     {BLD}{GRN} " + str(len(LOGRESULTS)) + " {RSC}TORRENTS{RST} match your TV series watchlist criteria\n").format(**AEC))
		i = 1
		for RESULT in LOGRESULTS:
			print((u"      {BLD}" + str(i).zfill(2) + "{RST}. " + RESULT).format(**AEC))[:89]
			i += 1
		print(u"")
	else:
		print((u"     {BLD}{YLW} {WARN} NO {RSC}TORRENTS{RST} match your TV series watchlist criteria").format(**AEC))


except:
	print((u"     {BLD}{YLW} {WARN} NO{RSC} TORRENTS{RST} can be matched.").format(**AEC))


###  TRANSMISSION REMOTE
if (ADDMAGNET == "ON"):
	
	try:
		subprocess.check_call("nc -w 3 -vz " + TRAN_HOST + " " + TRAN_PORT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
		if (os.path.getsize(TORRENTDB) > 0):
			with open(TORRENTDB, "r") as MAGNETDB:
				for TORR in MAGNETDB:
					TORR = TORR.strip()
					if len(TORR):
						TRANSMISSION = "transmission-remote " + TRAN_HOST + ":" + TRAN_PORT + " --auth " + USERNAME + ":" + PASSWORD + " --add " + TORR
						subprocess.call(TRANSMISSION,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
						
						###  Clear the magnet links database
						open(TORRENTDB, "w").close()
		
			print((u"     {BLD}{GRN} {PASS} {RSC}TORRENTS {GRN}ADDED{RST} remotely to Transmission Daemon").format(**AEC))	
	
	except:
		print((u"     {BLD}{RED} {ERROR} CONNECTION{RSC} to Transmission Daemon {RED}FAILED{RST}. Check RPC configuration.").format(**AEC))

### QUIT EVERYTHING, JUST IN CASE
quit(u"\n")

#
# EOF
#
