#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path, base64, time, feedparser, argparse
from urllib.request import Request, urlopen
from subprocess import call,PIPE

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
VERSION = "v3.1"

print((
 """{BLD}""" + PRONAME + """, """ + VERSION + """{RST} | TV Torrent Downloader

	Downloads matching TV Series titles from showrss.info and
	automatically queues the torrents to a running transmission daemon

	License  | Dio ( classicrocker384@gmail.com ), {UND}3-Clause BSD License{RST}
	Revision | """ + time.ctime(os.path.getmtime(__file__)) + """
	Depends  | python (base64, os.path, subprocess, time, feedparser, 
                   argparse, urllib.request), transmission-remote
	
 ------------------------------------------------------------------------------
 """).format(**AEC))

###  CONFIGURATION  ###############################################################################
DIRECTORY = os.path.dirname(__file__) + "/magnetic/"	# Absolute PATH of working directory
WATCHLIST = DIRECTORY + "series.db"			# TV SERIES watchlist
HASHESLOG = DIRECTORY + "torrent.log"			# History log of matched torrents w/ hashes
TORRENTDB = DIRECTORY + "torrent.db"			# Matched torrents database w/ magnet links
BLACKLIST = DIRECTORY + "blacklist.db"			# Do NOT download TORRENTS w/ these keywords

###  SETTINGS  ####################################################################################
RSSXMLURI = "https://showrss.info/other/all.rss"	# RSS2.0 XML URI
TOR_WRITE = "ON"					# Keep magnet URIs in Torrent DB   [ON|OFF]
LOG_WRITE = "ON"					# Keep torrents in history log     [ON|OFF]
DAYS2KEEP = "1"						# Clean history log after x days
BL_FILTER = "ON"					# Activate blacklist filter        [ON|OFF]

###  TRANSMISSION DAEMON  #########################################################################
ADDMAGNET = "ON"					# Add magnet URIs to transmission  [ON|OFF]
TRAN_HOST = "192.168.2.100"				# Transmission Daemon Host
TRAN_PORT = "9091"					# Transmission Daemon Port
USERNAME  = "transmission"				# Transmission Daemon Username
PASSWORD  = "yourpassword_base64_encoded"		# Transmission Daemon Password (base64)

###  DEFINE VARIABLES  ############################################################################
TVSERIESDB = []
TORRENT_DB = []
HISTORYLOG = []
FILTER_SPC = []
TORRENTSDT = {}
###################################################################################################


###  Create data directory for the script if it does not exist
if (not os.path.exists(DIRECTORY)):
	os.makedirs(DIRECTORY)

###  Print the WATCHLIST
print((u" :::  {BLD}TV SERIES WATCHLIST{RST}  ::::::::::::::::::::::::::::::::::::::::::::::::::::\n").format(**AEC))
try:
	with open(WATCHLIST, "r") as TVSERIES:
		###  Alphabetical listing of watchlist
		TVSERIESDB = list(sorted(TVSERIES.read().strip().splitlines()))
		
		if (os.path.getsize(WATCHLIST) > 0):
			def TVSERIESTITLES(l, n):
				for i in range(0, len(l), n):
					yield l[i:i+n]
			TVSERIESTITLES(TVSERIESDB,5)
				
			for TVSERIESTITLE in TVSERIESTITLES(TVSERIESDB,5):
				print(u"      " + ", ".join(TVSERIESTITLE))
		else:
			print((u"      {BLD}{YLW}{WARN}{RST} " + WATCHLIST + " is {BLD}{YLW}EMPTY{RST}").format(**AEC))
			print((u"      {BLD}{YLW}{WARN} ADD{RST} TV series titles, separated by a new line (e.g. Stranger Things)").format(**AEC))
			quit()
	print()
except IOError:
	open(WATCHLIST, "w").close()
	print((u"      {BLD}{RED}{ERROR}{RST} " + WATCHLIST + " was {BLD}{GRN}CREATED{RST}").format(**AEC))


###  PRINT BLACKLIST
if (BL_FILTER == "ON"):
	try:
		if (os.path.getsize(BLACKLIST) > 0):
			print((u"\n :::  {BLD}BLACKLIST{RST}  ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n").format(**AEC))
			
			with open(BLACKLIST, "r") as BLIST:
				BLACKLISTDB = list(sorted(BLIST.read().lower().strip().splitlines()))
				###  break the list every 5 keywords
				def BLACKLISTED(l, n):
					for i in range(0, len(l), n):
						yield l[i:i+n]
				BLACKLISTED(BLACKLISTDB,5)
				
				for KEYWORD in BLACKLISTED(BLACKLISTDB,5):
					print(u"      " + ", ".join(KEYWORD))
			print()
	except IOError:
		open(BLACKLIST, "w").close()
		print((u"      {BLD}{RED}{ERROR}{RST} " + BLACKLIST + " was {BLD}{GRN}CREATED{RST}").format(**AEC))


###  PRINT MATCHES
print((u"\n :::  {BLD}TV SERIES MATCHES{RST}  ::::::::::::::::::::::::::::::::::::::::::::::::::::::\n").format(**AEC))

###  if HASHESLOG has not been modified for more than x days, start CLEAN
if (LOG_WRITE == "ON"):
	
	### parse --clear-log 1 from the command line for debugging purposes
	parser = argparse.ArgumentParser()
	parser.add_argument('--clear-log', default=1)
	args = parser.parse_args()

	try:
		CUR_TIME = time.time()
		MOD_TIME = os.path.getmtime(HASHESLOG)
		
		if (CUR_TIME - MOD_TIME >= int(DAYS2KEEP) * 24 * 3600 or args.clear_log == "1"):
			open(HASHESLOG, "w").close()
			print((u"      {BLD}{YLW}{WARN}{RST} " + HASHESLOG + " was {BLD}{YLW}TRUNCATED{RST}\n").format(**AEC))
		
	except IOError:
		open(HASHESLOG, "w").close()
		print((u"      {BLD}{RED}{ERROR}{RST} " + HASHESLOG + " was {BLD}{GRN}CREATED{RST}\n").format(**AEC))

###  Check the RSS2.0 URI and parse the XML
try:
	### Open the RSS and store in variable
	XML = urlopen(Request(RSSXMLURI, headers={'User-Agent': 'Gecko/4.0'}),timeout=15).read()
	
	###  Parse the XML with Feedparser
	XML_PARSED = feedparser.parse(XML).entries
	
except:
	print((u"      {BLD}{RED}{ERROR}{RSC} HTTP {RED}TIMEOUT{RST} for URI " + RSSXMLURI + "\n").format(**AEC))
	quit()

try:
	for XMLENTRY in XML_PARSED:
		
		###  FETCH RSS VARIABLES
		XMLTITLE = XMLENTRY.title
		XML_FILE = XMLENTRY.tv_raw_title
		XML_HASH = XMLENTRY.tv_info_hash
		XML_MAGN = XMLENTRY.link
		
		for SERIES in TVSERIESDB:
			
			###  make SERIES TITLES lowercase for easier regex
			if (SERIES.lower() in XMLTITLE.lower()):
				
				###  DO NOT download FILTERED names
				if (BL_FILTER == "ON"):
					
					if (any(FILTER in XML_FILE.lower() for FILTER in BLACKLISTDB)):
						print((u"      {BLD}{CYN}{WARN} FILTERED{RST} | " + XML_FILE[:58]).format(**AEC))
						continue
				
				###  in the off-chance that NO MAGNET URI in the XML, filter out the problematic torrent
				if (XML_MAGN == ""):
					print((u"      {BLD}{RED}{ERROR} NOMAGNET{RST} | " + XML_FILE[:58]).format(**AEC))
					continue
				
				###  Load historical hashes
				with open(HASHESLOG, "r") as HISTORY:
					for HASH in HISTORY:
						HASH = HASH.strip()
						if len(HASH):
							HISTORYLOG.append(HASH)
				
				###  Check the HISTORY LOG for already downloaded torrents
				if (XML_HASH in HISTORYLOG):
					print((u"      {BLD}{YLW}{WARN} EXISTING{RST} | " + XML_FILE[:58]).format(**AEC))
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
	print()
	
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
				print((u"      {BLD}{RED}{ERROR}{RST} " + TORRENTDB + " was {BLD}{RED}NOT ACCESSIBLE{RST}").format(**AEC))
				
			
		### Write the HISTORY LOG. We DO NOT WANT to DOWNLOAD torrents twice
		if (LOG_WRITE == "ON"):
			try:
				with open(HASHESLOG, "w") as LOGDB:
					for HASH in HISTORYLOG:
						LOGDB.write(HASH + "\n")
			
			except IOError:
				print((u"      {BLD}{RED}{ERROR}{RST} " + HASHESLOG + " was {BLD}{RED}NOT ACCESSIBLE{RST}").format(**AEC))
				
		###  TITLES of TORRENT DOWNLOADS
		LOGRESULTS.append(TORRENTSDT[TOR]["TITLE"])
		

	###  PRINT TV SERIES MATCHES
	if len(LOGRESULTS):
		i = 1
		for RESULT in LOGRESULTS:
			print((u"      {BLD}{GRN}{PASS} ADD {RSC}(" + str(i).zfill(2) + "){RST} | " + RESULT[:58]).format(**AEC))
			i += 1
	else:
		print((u"      {BLD}{YLW}{WARN} NO MATCH{RST} | No more torrents match your TV series watchlist.").format(**AEC))

except:
	print((u"      {BLD}{RED}{ERROR}{RSC} Something went {RED}WRONG{RSC}. Maybe check RSS field names.{RST}\n").format(**AEC))
	quit()

###  TRANSMISSION REMOTE
if (ADDMAGNET == "ON"):
	print()
	try:
		with open(TORRENTDB, "r") as MAGNETDB:
			
			for TORR in MAGNETDB:
				TORR = TORR.strip()
				if len(TORR):
					
					TRANSMISSION = "transmission-remote " + TRAN_HOST + ":" + TRAN_PORT + " --auth " + USERNAME + ":" + str(base64.urlsafe_b64decode(PASSWORD), "ascii") + " --add " + TORR
					subprocess.call(TRANSMISSION,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
					
					###  Clear the magnet links database
					open(TORRENTDB, "w").close()
	except IOError:
		open(TORRENTDB, "w").close()
		print((u"      {BLD}{RED}{ERROR}{RST} " + TORRENTDB + " was {BLD}{GRN}CREATED{RST}\n").format(**AEC))
	except:
		print((u"      {BLD}{RED}{ERROR}{RSC} Remote connection to Transmission RPC {RED}FAILED{RST}.\n          Check configuration.\n          Magnet links should still be safely stored.\n").format(**AEC))

### QUIT EVERYTHING, JUST IN CASE
quit()

#
# EOF
#
