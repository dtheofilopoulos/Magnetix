# magneticEZTV
Downloads matching TV Series titles as soon as they air on eztv and automatically queues the torrents to a running transmission daemon

Add TV series titles in series.db separated by a new line everytime.
Tweak any settings you might need and run the python script.
You should be able to collect matching magnet links in torrent.db

# Transmission Daemon
When torrent magnet links are present in torrent.db, magnet links will be passed on to transmission daemon.
Transmission remote is required for this to work. If successful, torrent.db will be truncated.

# Cronjob
You can then add the script to a cronjob (i.e. every five minutes) and let the magic happen.

*/5    *      *      *      *      /pathtoscript/eztv.py
