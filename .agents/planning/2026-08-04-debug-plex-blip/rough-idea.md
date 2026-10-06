# DEBUG Plex blip

Plex had another random blip just around 0700 EDT this morning where the stream stopped and the plex server couldn't be reached at all.

The logs can be found in /tmp/plex-logs/ and grafana clearly shows a few interesting data points
- There is a hearbeat blip around that time starting around 06:59:15
- There is a mild CPU "spike" which pushes utilisation up to ~30% just before

Traefik logs don't show anything and Plex logs also don't seem to show anything either.

## Objective

The primary objective is to find the root cause and fix it *BUT* the task at hand is to first figure out how to track this down as this has happened multiple times but is sporadic.
