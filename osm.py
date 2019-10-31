#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import io
import ioutils


coordinates = {
    u"D W Flobecks Plats": u"{{Coord|57|42|1.68|N|11|54|31.08|E|name=D W Flobecks Plats (plats) - Källa: Stadsbyggnadskontoret Göteborg}}",
    u"Färjenästerrassen": u"{{Coord|57|41|50.56|N|11|54|23.31|E|name=Färjenästerrassen (plats) - Källa: Stadsbyggnadskontoret Göteborg}}",
    u"Pölsebobacken": u"{{Coord|57|41|59.43|N|11|54|25.55|E|name=Pölsebobacken (plats) - Källa: Stadsbyggnadskontoret Göteborg}}",
    u"Lapparns Lycka": u"{{Coord|57|47|44.3|N|12|8|34.5|E|name=Lapparns Lycka (väg) - Källa: Gissning}}",
    u"Lilla Sparvgatan": u"{{Coord|57|43|8.40|N|12|0|13.82|E|name=Lilla Sparvgatan (gata) - Källa: Gissning}}",
    u"Ringlinieplatsen": u"{{Coord|57|42|35.68|N|11|59|32.90|E|name=Ringlinieplatsen (plats) - Källa: Gissning}}",
    u"Sörmarkavägen": u"{{Coord|57|44|4.55|N|11|48|9.47|E|name=Sörmarkavägen (gata) - Källa: Grov gissning}}",
    u"Torrdockan": u"{{Coord|57|41|50.49|N|11|54|35.75|E|name=Torrdockan (plats) - Källa: Gissning}}",
    u"Redareparken": u"{{coord|57|42|13.8|N|11|57|16.4|E|name=Redareparken (park) - Källa: Gissning}}",
    u"Skeppsbropiren": u"{{coord|57|42|11.3|N|11|57|11.7|E|name=Skeppsbropiren (pir) - Källa: Gissning}}",
    u"Skallgången": u"{{Coord|57|36|50.50|N|11|56|40.58|E|name=Skallgången (gångstig) - Källa: Gissning}}",
    u"Bergslagsmotet": u"{{coord|57|42|43.0|N|11|58|19.0|E|name=Bergslagsmotet (mot) - Källa: Gissning}}",
    u"Falutorgsmotet": u"{{coord|57|43|0.2|N|11|58|56.0|E|name=Falutorgsmotet (mot) - Källa: Gissning}}",
    u"Forthamnsvägen": u"{{Coord|57|40|35.4|N|11|51|14.0|E|name=Forthamnsvägen (väg) - Källa: Gissning}}",
    u"Radarhöjden": u"{{Coord|57|40|37.7|N|11|51|31.8|E|name=Radarhöjden (plats) - Källa: Gissning}}",
    u"Kolhyvarestigen": u"{{Coord|57|40|29.19|N|11|51|52.14|E|name=Kolhyvarestigen (stig) - Källa: Gissning}}",
    u"Fagerdalsparken": u"{{Coord|57|48|14.4|N|11|58|15.4|E|name=Fagerdalsparken (park) - Källa: Gissning}}",
}

blacklisted_osm_ids = {
    245689491: u"'Trappstigen' should be in Hammarkullen according to description, but this id is in Kållered",
}

cached_osm_responses = {}
osm_responses_file = "osm_responses.txt"

nominatim_url = "http://nominatim.openstreetmap.org/search?" \
                "format=json&bounded=1&viewbox=11.6000,57.5000,12.3000,57.9000&q="


def get_osm_response(feature_name):
    global cached_osm_responses

    if feature_name in cached_osm_responses:
        json_response = cached_osm_responses[feature_name]

    elif not ioutils.file_exists(osm_responses_file) or ioutils.file_is_older_than_one_day(osm_responses_file):
        json_response = download_response(feature_name)

    else:
        with io.open(osm_responses_file, "r", encoding="utf-8") as my_file:
            file_content = my_file.read()
            json_content = ioutils.read_json_string(file_content)

            if feature_name in json_content:
                json_response = json_content[feature_name]
            else:
                json_response = download_response(feature_name)

    cached_osm_responses[feature_name] = json_response
    return ioutils.read_json_string(json_response)


def download_response(feature_name):
    return requests.get(nominatim_url + feature_name.replace(" ", "%20")).text


def is_hardcoded(feature_name):
    return feature_name in coordinates


def get_hardcoded_value(feature_name):
    return coordinates[feature_name]


def is_blacklisted(osm_id):
    return osm_id in blacklisted_osm_ids


def get_blacklist_reason(osm_id):
    return blacklisted_osm_ids[osm_id]
