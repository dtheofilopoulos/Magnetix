# magnetic
Downloads matching TV Series titles from https://showrss.info/ and automatically queues the torrents to a running transmission daemon (https://transmissionbt.com/about/).

Add TV series titles in series.db separated by a new line everytime.

ie. Lucifer
    Stranger Things
    The Walking Dead
    ... and so on
    
    
I tried to write this python script with the most minimal approach to dependencies. There is no need to pip install. Just download, change permissions to u+w and run.

I am aware that there may still be some bugs, which I am going to do my best to fix, however, this little script has been serving me well for about 3 years now.
Please comment or suggest future features if you find this useful, or report any bugs you may have encountered.

This is a raspberry pi project I have been working on to work seemlessly with my Synology NAS and I wanted something as lightweight as possible.
Tweak any settings you might need and run the python script.
You should be able to collect matching magnet links in torrent.db

# Transmission Daemon
When torrent magnet links are present in torrent.db, magnet links will be passed on to a running transmission daemon. Change settings accordingly to match your setup.
Transmission remote is required for this to work. If successful, torrent.db will be truncated.

# Cronjob
You can then add the script to a cronjob (i.e. every five minutes) and allow it to run automagically.

*/5    *      *      *      *      /pathtoscript/magnetic.py
