# wikipedia_streetname_filter

##Background
One part of city planning consists of the local authorities having meetings where they establish names for streets, squares etc. that are to be built. People of the Swedish Wikipedia community have gone through the protocols from these meetings from the local authorities of the city of Gothenburg. This has resulted in [a fairly large list of street names](https://sv.wikipedia.org/wiki/Gatunamn_i_G%C3%B6teborg_fr%C3%A5n_och_med_2001) that have been added to the city since 2001.

[Open Street Map](https://www.openstreetmap.org) is a project to create free maps for the entire world. This script will parse the wikipedia list of street names in Gothenburg and check if they are present in Open Street Map. The streets that are present will be filtered away, so that only the streets that are not present in Open Street Map remain. This sub-list of streets is not intended to replace the original list, but is meant to be manually inspected so that the missing street names can be added to Open Street Map when possible.

##How to run

Make sure you have Python3 and start `streetname_filter.py`.
