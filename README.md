# magnetic
Magnetic is a non-ads crawler matching a list of your predefined TV Series titles. It will fetch their magnet urls from https://showrss.info/ and automatically queue them to transmission RPC (https://transmissionbt.com/about/).

I tried to write this python script with the most minimal approach to dependencies. There is no need to pip install. Just download, change permissions to u+w, add TV series titles in series.db, separated by a new line everytime. Change settings accordingly to match your setup and run the python script.
You should be able to collect matching magnet links in torrent.db. In order to avoid duplicates, hashes are kept for 1 day (you can change that to whatever suits your needs best). Additionally, you can specify keywords in blacklist.db to filter unwanted matches.

# Settings

TOR_WRITE = "ON"                                        # Keep magnet URIs in Torrent DB   [ON|OFF]

LOG_WRITE = "ON"					# Keep torrents in history log     [ON|OFF]

DAYS2KEEP = "1"						# Clean history log after x days

BL_FILTER = "ON"					# Activate filter                  [ON|OFF]

ADDMAGNET = "ON"					# Add magnet URIs to transmission  [ON|OFF]

TRAN_HOST = "192.168.2.100"				# Transmission Daemon Host

TRAN_PORT = "9091"					# Transmission Daemon Port

USERNAME  = "transmission"				# Transmission Daemon Username

PASSWORD  = "yourpassword"				# Transmission Daemon Password (base64 encoded)


# Transmission Daemon
Optionally, you can use this script to connect to a running transmission RPC. Transmission remote (https://linux.die.net/man/1/transmission-remote) is required for this to work).
If you do not have one installed, remember to switch the ADDMAGNET option to OFF. Either way, torrent magnet links will be populated in torrents.db for your personal use.
When torrent magnet links are present in torrent.db, magnet links can be passed on to transmission (ADDMAGNET needs to be set to ON for this to function).
If successful, torrent.db will be automatically truncated.

# Cronjob
Optionally, you can add the script to a cronjob (i.e. every five minutes) and allow it to automagically run.

*/5    *      *      *      *      /pathtoscript/magnetic.py

# Bugs & Reports
I am aware that there may still be some bugs, which I am going to do my best to fix, however, this little script has been serving me well for about 3 years now.
This is a raspberry pi project I have been working on to work seemlessly with my Synology NAS, hence I wanted something as lightweight as possible.
Please comment or suggest future features if you find this useful, or report any bugs you may have encountered.
