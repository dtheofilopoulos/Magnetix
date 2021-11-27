# magnetic
Downloads matching TV Series titles from https://showrss.info/ and automatically queues the torrents to a running transmission daemon (https://transmissionbt.com/about/).

I tried to write this python script with the most minimal approach to dependencies. There is no need to pip install. Just download, change permissions to u+w, add TV series titles in series.db separated by a new line everytime. Change settings accordingly to match your setup and run the python script.
You should be able to collect matching magnet links in torrent.db

# Transmission Daemon
When torrent magnet links are present in torrent.db, magnet links will be passed on to a running transmission daemon. 

Transmission remote is required for this to work. If successful, torrent.db will be truncated.
I am aware that there may still be some bugs, which I am going to do my best to fix, however, this little script has been serving me well for about 3 years now.
This is a raspberry pi project I have been working on to work seemlessly with my Synology NAS and I wanted something as lightweight as possible.
Please comment or suggest future features if you find this useful, or report any bugs you may have encountered.

# Cronjob
Optionally, you can add the script to a cronjob (i.e. every five minutes) and allow it to automagically run.

*/5    *      *      *      *      /pathtoscript/magnetic.py
