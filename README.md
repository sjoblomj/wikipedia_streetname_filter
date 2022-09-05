# wikipedia_streetname_filter

## Background
One part of city planning consists of the local authorities having meetings where they establish names for streets, squares etc. that are to be built. People of the Swedish Wikipedia community have gone through the protocols from these meetings from the local authorities of the city of Gothenburg. This has resulted in [a fairly large list of street names](https://sv.wikipedia.org/wiki/Gatunamn_i_G%C3%B6teborg_fr%C3%A5n_och_med_2001) that have been added to the city since 2001.

[Open Street Map](https://www.openstreetmap.org) is a project to create free maps for the entire world (sometimes referred to as the "Wikipedia of maps").

## Script
The Wikipedia Streetname Filter is a script will parse the wikipedia list of street names in Gothenburg and check if they are present in Open Street Map. The streets that are present will be filtered away, so that only the streets that are not present in Open Street Map remain. This sub-list of streets is not intended to replace the original list, but is meant to be manually inspected so that the missing street names can be added to Open Street Map when possible.

## dbserver
The progam will send a REST-request for each street in the list, which might flood the Open Street Map servers and cause it to deny requests. Therefore, a dbserver is included, which acts as a server that can answer queries on whether or not a given feature in Open Street Map exists and is within the greater city of Gothenburg.

The dbserver needs to be given the raw Open Street Map data for extraction. The easiest way to obtain that is from [Geofabrik](https://geofabrik.de), which provides the data of [Sweden](https://download.geofabrik.de/europe/sweden.html) for download. The file sweden-latest.osm.pbf needs to be downloaded, which is roughly 600 mb.

The dbserver is built using Kotlin and requires a postgis database, which can be started using docker-compose.

## Requirements
To run everything, the following software needs to be installed:
* docker-compose
* Java 17
* Maven
* Python3
* curl

## How to run
A convenience script is provided that will set up the database, build the dbserver, download the Open Street Map data of Sweden, populate the database and finally run the script to compare the Wikipedia list with the Open Street Map data. Simply start the script by running `./run.sh`.

### Manually running
If, instead of running the `run.sh` convenience script, one wishes to manually start the postgis database, start up the dbserver and populate it, do the following:
```
docker-compose up -d
cd dbserver
mvn clean install
curl -s -o sweden-latest.osm.pbf https://download.geofabrik.de/europe/sweden-latest.osm.pbf  # This file is approximately 600 mb!
java -jar target/dbserver-0.0.1-SNAPSHOT.jar
curl -X POST http://localhost:7171/consume?filename=sweden-latest.osm.pbf
```

Wait until the dbserver outputs "All done!", which will take a fairly long time. Now that there is a local server that can answer queries, a new terminal window can be opened and the script started by running `./streetname_filter.py`
