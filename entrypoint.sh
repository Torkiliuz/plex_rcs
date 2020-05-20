#!/bin/ash

DELAY=5m

# Now execute the sync script in a loop, waiting DELAY before running again
while true
do
	python /plex_rcs/plex_rcs.py
	sleep $DELAY
done
