#!/usr/bin/env python
# coding=utf8
import os.path,time,urllib2,feedparser

###  Created by Dio Theofilopoulos ( classicrocker384@gmail.com )  ################################

###  CONFIGURATION  ###############################################################################
DIRECTORY = os.path.dirname(__file__) + "/"		# Absolute PATH of working directory
WATCHLIST = DIRECTORY + "series.db"			# TV SERIES watchlist
TORRENTDB = DIRECTORY + "torrent.db"			# Matched torrents database w/ magnet links
HASHESLOG = DIRECTORY + "torrent.log"			# History log of matched torrents w/ hashes

###  SETTINGS  ####################################################################################
RSSXMLURI = "https://eztv.io/ezrss.xml"			# RSS2.0 XML URI
CLEANHASH = "YES"					# Clean hashes after 2 days        [YES|NO]
TOR_WRITE = "YES"					# Write Torrent DB magnet URIs     [YES|NO]
LOG_WRITE = "YES"					# Write downloaded torrents log    [YES|NO]
FILTERSTR = ("480p","720p","1080p",".avi$","iP.WEB-DL")	# Do NOT download FILENAMES w/ these tags


###  DEFINE VARIABLES
TVSERIESDB = []
TORRENT_DB = []
HISTORYLOG = []
TORRENTSDT = {}


###  if HASHESLOG has not been modified for more than 2 days, start CLEAN
if CLEANHASH == "YES":
	try:
		CUR_TIME = time.time()
		MOD_TIME = os.path.getmtime(HASHESLOG)
	
		if (CUR_TIME - MOD_TIME >= 2 * 24 * 3600):
			
			open(HASHESLOG, "w").close()
			print(u"     \033[1m\033[93m \u26a0 \033[0m" + HASHESLOG + " was \033[1mTRUNCATED\033[0m")
	
	except:
		print(u"     \033[1m\033[91m \u2716 \033[0m" + HASHESLOG + " was \033[1m\033[91mNOT ACCESSIBLE\033[0m")
		open(HASHESLOG, "w").close()
		print(u"     \033[1m\033[91m \u2716 \033[0m" + HASHESLOG + " was \033[1mCREATED\033[0m\n")


###  Check the WATCHLIST making TITLES lowercase for easier comparison
try:
	LIST = open(WATCHLIST, "r")
	for SERIES in LIST:
		SERIES = SERIES.strip()
		if len(SERIES):
			TVSERIESDB.append(SERIES.lower())
	LIST.close()
	
	###  Print the WATCHLIST
	print(u"\n :::  \033[1mTV SERIES WATCHLIST\033[0m  ::::::::::::::::::::::::::::::::::::::::::::::::::::\n")

	if (os.path.getsize(WATCHLIST) > 0):
		print(os.popen("more -scfl " + WATCHLIST + " | sort -ubdfV | cut -c -17 | sed -e 's/^/      /g' | column -c 74").read())
	else:
		print(u"     \033[1m\033[93m \u26a0 \033[0m" + WATCHLIST + " is \033[1m\033[93mEMPTY\033[0m")
		print(u"     \033[1m\033[93m \u26a0 ADD\033[0m TV series titles, separated by a new line (e.g. Family Guy)\n")
	
except IOError:
	print(u"     \033[1m\033[91m \u2716 \033[0m" + WATCHLIST + " was \033[1m\033[91mNOT ACCESSIBLE\033[0m")
	open(WATCHLIST, "w").close()
	print(u"     \033[1m\033[91m \u2716 \033[0m" + WATCHLIST + " was \033[1mCREATED\033[0m")


print(u"\n :::  \033[1mTV SERIES MATCHES\033[0m  ::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
###  Check the EZTV RSS2.0 URI and parse the XML
try:
	URIHEADER = { "User-Agent": "Links (2.7; Linux; text)", "Content-Type": "text/xml", "pragma-directive": "no-cache" }
	XML = urllib2.urlopen(urllib2.Request(RSSXMLURI, headers=URIHEADER), timeout=15)
	
	###  Parse the XML for a limit of 50 entries
	XML_PARSED = feedparser.parse(XML).entries[:50]
	
except:
	print(u"     \033[1m\033[91m \u2716 \033[0m\033[1mHTTP STATUS \033[91m408\033[0m for URI \033[1m" + str(RSSXMLURI) + "\033[0m")


try:
	for XMLENTRY in XML_PARSED:
		for SERIES in TVSERIESDB:
			
			###  FETCH RSS VARIABLES
			XMLTITLE = str(XMLENTRY.title)
			XML_FILE = str(XMLENTRY.torrent_filename)
			XML_HASH = str(XMLENTRY.torrent_infohash)
			XML_MAGN = str(XMLENTRY.torrent_magneturi)
			
			###  make EZTV SERIES TITLES lowercase for easier comparison
			if SERIES.lower() in XMLTITLE.lower():
							
				###  DO NOT download FILTERED names (using filename for consistency reasons)
				if any(FILTER in XML_FILE for FILTER in FILTERSTR):
					i = 1
					print(u"      \033[1m\033[93m\u26a0\033[0m \033[1mFILTERED [" + str(i).zfill(2) + "]\033[0m: " + XML_FILE)[:96] + " ..."
					i += 1
					continue
				
				###  in the off-chance that NO MAGNET URI in the XML
				if XML_MAGN == "":
					i = 1
					print(u"      \033[1m\033[91m\u2716\033[0m \033[93m\033[1mNO\033[0m\033[1m MAGNET URI [" + str(i).zfill(2) + "]\033[0m: " + XMLTITLE)[:96] + " ..."
					i += 1
					continue
				
				###  Check for existing TORRENT HASHES
				HISTORY = open(HASHESLOG, "r")
				for HASH in HISTORY:
					HASH = HASH.strip()
					if len(HASH):
						HISTORYLOG.append(HASH)
				HISTORY.close()
				
				###  CHECK THE HISTORY LOG FOR EXISTING HASHES
				if XML_HASH in HISTORYLOG:
					continue
				else:
					HISTORYLOG.append(XML_HASH)
				
				###  Check for existing MAGNET LINKS
				if XML_MAGN in TORRENT_DB:
					continue
				else:
					TORRENT_DB.append(XML_MAGN)
				
				###  Build the array with UNIQUE torrent matches based on infohash
				TORRENTSDT[XML_HASH] = { "TITLE": XMLTITLE, }
	
	
	###  WRITE LOGS FOR MATCHED TORRENTS
	LOGRESULTS = []
	for TOR in TORRENTSDT:
		### Write the TORRENT LOG. Append MAGNET URIs for MATCHED TORRENTS
		if TOR_WRITE == "YES":
			try:
				MAGNETDB = open(TORRENTDB, "w")
				for MAGNETURI in TORRENT_DB:
					MAGNETDB.write(MAGNETURI + "\n")
				MAGNETDB.close()
			
			except IOError:
				quit(u"     \033[1m\033[91m \u2716 \033[0m" + TORRENTDB + " was \033[1m\033[91mNOT ACCESSIBLE\033[0m")
			
			
		### Write the HISTORY LOG. We DO NOT WANT to DOWNLOAD torrents twice
		if LOG_WRITE == "YES":
			try:
				LOGDB = open(HASHESLOG, "w")
				for HASH in HISTORYLOG:
					LOGDB.write(HASH + "\n")
				LOGDB.close()
			
			except IOError:
				quit(u"     \033[1m\033[91m \u2716 \033[0m" + HASHESLOG + " was \033[1m\033[91mNOT ACCESSIBLE\033[0m")
		
		###  TITLES of TORRENT DOWNLOADS
		LOGRESULTS.append(TORRENTSDT[TOR]["TITLE"])
		

	###  PRINT TV SERIES MATCHES
	if LOGRESULTS:
		print(u"\n     \033[1m\033[91m " + str(len(LOGRESULTS)) + " \033[0m\033[1mTORRENTS\033[0m match your TV series watchlist\n")
		i = 1
		for RESULT in LOGRESULTS:
			print(u"      \033[1m" + str(i).zfill(2) + "\033[0m. " + RESULT)
			i += 1
	else:
		print(u"\n     \033[1m\033[93m \u26a0 NO \033[0m\033[1mTORRENTS\033[0m match your TV series watchlist\n")

except:
	print(u"     \033[1m\033[91m \u2716 ERROR\033[0m: CANNOT match torrents.\n")

### QUIT EVERYTHING, JUST IN CASE
quit(u"")

#
# EOF
#