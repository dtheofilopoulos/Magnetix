# magneticEZTV
Downloads matching TV Series titles as soon as they air on eztv and automatically queues them in transmission daemon

Add series TV titles in series.db separated with a new line everytime.
Tweak any settings you might need and run the python script.
You should be able to collect matching magnet links in torrent.db

When torrent magnet links are present in torrent.db, magnet links will be passed on to transmission daemon.
Transmission remote is required for this to work. If successful, torrent.db will be truncated.

You can then add the script to a cronjob and let the magic happen.
