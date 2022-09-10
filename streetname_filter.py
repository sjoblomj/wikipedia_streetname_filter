#!/usr/bin/env python
# -*- coding: utf-8 -*-

import operator
import json
import sys
import wikipedia
import osm
import ioutils
from termcolor import colored

errors_not_way = []
errors_wrong_name = []
errors_is_blacklisted = []

missing_features_file = "missing_features_in_osm.txt"
updated_wikipedia_content = "updated_wikipedia_content.txt"


def is_present_in_map(osm_response_list, feature_name, feature_type):
    global errors_not_way
    global errors_wrong_name
    global errors_is_blacklisted
    not_way = []
    wrong_name = []
    is_blacklisted = []

    for osm_result in osm_response_list:
        if not has_correct_name(osm_result, feature_name):
            wrong_name.append(colored(feature_name, "red") + " (" + colored(feature_type, "yellow") + ") - " +
                              "osm_type:'" + colored(osm_result["osm_type"], "blue") + "', " +
                              "display_name:'" + colored(osm_result["display_name"], "blue") + "', " +
                              "osm_id:" + colored(str(osm_result["osm_id"]), "blue"))
            continue

        if not is_of_accepted_type(osm_result, feature_type):
            not_way.append(colored(feature_name, "red") + " (" + colored(feature_type, "yellow") + ") - " +
                           "osm_type:'" + colored(osm_result["osm_type"], "blue") + "', " +
                           "type:'" + colored(osm_result["type"], "blue") + "', " +
                           "class:'" + colored(osm_result["class"], "blue") + "', " +
                           "display_name:'" + colored(osm_result["display_name"], "blue") + "', " +
                           "osm_id:" + colored(str(osm_result["osm_id"]), "blue"))
            continue

        if osm.is_blacklisted(osm_result["osm_id"]):
            is_blacklisted.append(colored(feature_name, "red") + " (" + colored(feature_type, "yellow") + ") - " +
                                  "osm_id:" + colored(str(osm_result["osm_id"]), "blue") + ", " +
                                  "Reason for blacklisting: " +
                                  colored(osm.get_blacklist_reason(osm_result["osm_id"]), "blue"))
            continue

        return True

    errors_not_way += not_way
    errors_wrong_name += wrong_name
    errors_is_blacklisted += is_blacklisted
    return False


def get_coordinates_of_correct_feature(osm_response_list, feature_name, feature_type):
    for osm_result in osm_response_list:
        if is_of_accepted_type(osm_result, feature_type) and has_correct_name(osm_result, feature_name):
            return osm_result["lat"], osm_result["lon"]
    return "", ""


def is_feature_decommissioned(wp_data):
    return u"avregistrerat" in wp_data[u"fastställd"]


def is_accepted_type(osm_result, feature_type, accepted_result_type, accepted_feature_type):
    return osm_result["type"] == accepted_result_type and feature_type == accepted_feature_type


def is_of_accepted_type(osm_result, feature_type):
    return is_accepted_type_for_way(osm_result, feature_type) or \
           is_accepted_type_for_node(osm_result, feature_type) or \
           is_accepted_type_for_relation(osm_result, feature_type)


def is_accepted_type_for_way(osm_result, feature_type):
    return osm_result["osm_type"] == "way" and \
           osm_result["type"] != "motorway_junction" and \
           osm_result["type"] != "water" and \
           feature_type != "mot"


def is_accepted_type_for_node(osm_result, feature_type):
    accepted_types = [                         \
        ("motorway_junction", "mot"),          \
        ("neighbourhood", "plats"),            \
        ("isolated_dwelling", "plats"),        \
        ("locality", "plats"),                 \
        ("locality", "park"),                  \
        ("locality", "backe"),                 \
        ("hamlet", "område"),                  \
    ]

    has_accepted_type = any(list(map(lambda x: is_accepted_type(osm_result, feature_type, x[0], x[1]), accepted_types)))
    return osm_result["osm_type"] == "node" and has_accepted_type


def is_accepted_type_for_relation(osm_result, feature_type):
    accepted_types = [                         \
        ("park", "park"),                      \
        ("track", "idrottsplan"),              \
        ("sports_centre", "idrottsplan"),      \
        ("sports_centre", "idrottsanläggning"),\
        ("meadow", "område"),                  \
        ("forest", "park"),                    \
        ("forest", "dalgång"),                 \
        ("scrub", "park"),                     \
        ("wood", "skog"),                      \
        ("square", "torg"),                    \
        ("square", "plats"),                   \
        ("square", "väg"),                     \
        ("pedestrian", "plats"),               \
        ("grass", "plats"),                    \
        ("recreation_ground", "plats"),        \
    ]

    has_accepted_type = any(list(map(lambda x: is_accepted_type(osm_result, feature_type, x[0], x[1]), accepted_types)))
    return osm_result["osm_type"] == "relation" and has_accepted_type


def has_correct_name(osm_result, feature_name):
    return osm_result["display_name"].lower().startswith(feature_name.lower() + ",")


def decdeg2dms(dd):
    mnt, sec = divmod(dd * 3600, 60)
    deg, mnt = divmod(mnt, 60)
    return str(int(deg)), str(int(mnt)), str(sec)[0:5]


def attempt_to_update_coordinates_from_osm(feature_name, feature_type, osm_response_list, wp_data):
    lat, lon = get_coordinates_of_correct_feature(osm_response_list, feature_name, feature_type)
    if wp_data['koordinater'] == "" and lat != "" and lon != "":

        latdeg, latmnt, latsec = decdeg2dms(float(lat))
        londeg, lonmnt, lonsec = decdeg2dms(float(lon))
        return "{{coord|" + latdeg + "|" + latmnt + "|" + latsec + "|N|" + londeg + "|" + lonmnt + "|" + lonsec + \
               "|E|name=" + feature_name + " (" + wp_data['typ'] + ")}}"

    return wp_data['koordinater']


def get_missing_features(wp_data_list):
    errors_superfluous_hardcoded_coordinate = []

    has_coordinates = 0
    lacks_coordinates = 0
    type_counter = {}
    i = 1

    for wp_data in wp_data_list:
        feature_name = wikipedia.remove_links(wp_data['gatunamn'])

        sys.stdout.write(" On feature %-50s %d of %d (%d%%)\r" % (colored(feature_name, "red"), i, len(wp_data_list),
                                                                 i * 100 / len(wp_data_list)))
        sys.stdout.flush()
        i += 1

        if is_feature_decommissioned(wp_data):
            wikipedia.print_json_to_file(updated_wikipedia_content, wp_data)
            continue

        feature_type = wikipedia.remove_links(wp_data["typ"])
        osm_response = osm.get_osm_response(feature_name)

        if feature_name.startswith("S:t ") and \
                is_present_in_map(osm.get_osm_response(feature_name.replace("S:t ", "Sankt ", 1)),
                                  feature_name.replace("S:t ", "Sankt ", 1), feature_type):

            feature_name = feature_name.replace("S:t ", "Sankt ", 1)
            osm_response = osm.get_osm_response(feature_name)

            errors_superfluous_hardcoded_coordinate = \
                update_when_present_in_map(feature_type, osm_response, wp_data, feature_name,
                                           errors_superfluous_hardcoded_coordinate)

        elif is_present_in_map(osm_response, feature_name, feature_type):

            errors_superfluous_hardcoded_coordinate = \
                update_when_present_in_map(feature_type, osm_response, wp_data, feature_name,
                                           errors_superfluous_hardcoded_coordinate)

        else:
            wikipedia.print_json_to_file(updated_wikipedia_content, wp_data)

            if wp_data['koordinater'] != "":
                if "|name=" in wp_data['koordinater']:
                    wp_data['koordinater'] = wp_data['koordinater'].replace("}}", u" - Källa: WP}}")
                else:
                    wp_data['koordinater'] = wp_data['koordinater'] \
                        .replace("}}", u"|name=" + feature_name + " (" + wp_data['typ'] + ") - Källa: WP}}")
            elif osm.is_hardcoded(feature_name):
                wp_data['koordinater'] = osm.get_hardcoded_value(feature_name)

            wikipedia.print_json_to_file(missing_features_file, wp_data)
            has_coordinates, lacks_coordinates = \
                gather_statistics(feature_type, has_coordinates, lacks_coordinates, wp_data, type_counter)

    print_statistics(has_coordinates, lacks_coordinates, errors_superfluous_hardcoded_coordinate, type_counter)


def update_when_present_in_map(feature_type, osm_response_list, wp_data, feature_name,
                               errors_superfluous_hardcoded_coordinate):

    wp_data['koordinater'] = attempt_to_update_coordinates_from_osm(
        feature_name, feature_type, osm_response_list, wp_data)

    wikipedia.print_json_to_file(updated_wikipedia_content, wp_data)

    if osm.is_hardcoded(feature_name):
        coloured_name_and_type = colored(feature_name, "red") + " (" + colored(feature_type, "yellow") + ")"
        errors_superfluous_hardcoded_coordinate += [coloured_name_and_type]
    return errors_superfluous_hardcoded_coordinate


def gather_statistics(feature_type, has_coordinates, lacks_coordinates, wp_data, type_counter):
    if feature_type in type_counter:
        type_counter[feature_type] = type_counter[feature_type] + 1
    else:
        type_counter[feature_type] = 1
    if wp_data['koordinater'] != "":
        has_coordinates += 1
    else:
        lacks_coordinates += 1
    return has_coordinates, lacks_coordinates


def print_statistics(has_coordinates, lacks_coordinates, errors_superflous_hardcoded_coordinate, type_counter):
    sorted_types = sorted(type_counter.items(), key=operator.itemgetter(1))
    print("\n")
    print("Total amount of features not present on OSM: " + colored(str(has_coordinates + lacks_coordinates), "red"))
    print("Amount of the total that has  coordinates: " + colored(str(has_coordinates), "red"))
    print("Amount of the total that lack coordinates: " + colored(str(lacks_coordinates), "red"))

    print("\nThese are the types:")
    for tup in sorted_types:
        num = colored("{:>3}".format(str(tup[1])), "red")
        feature_type = colored(tup[0], "yellow")
        print(num + ": " + feature_type)

    if len(errors_not_way) > 0:
        print("\n\nThese results from OSM have the name asked for, but not the right type:")
        for error in errors_not_way:
            print(error)
    if len(errors_wrong_name) > 0:
        print("\n\nThese results from OSM almost but not exactly matched the name asked for:")
        for error in errors_wrong_name:
            print(error)
    if len(errors_is_blacklisted) > 0:
        print("\n\nThese results from OSM have the name asked for, but are blacklisted:")
        for error in errors_is_blacklisted:
            print(error)
    if len(errors_superflous_hardcoded_coordinate) > 0:
        print("\n\nThese coordinates have been hardcoded in, but they are already present in OSM:")
        for error in errors_superflous_hardcoded_coordinate:
            print(error)

    print("\n")
    print("The features not present in OSM have been written to " + colored(missing_features_file, "blue"))
    print("The original Wikipedia page has been formatted, and features without coordinates on the Wikipedia page "
          "have had their coordinates looked up from OSM. The result has been written to " +
          colored(updated_wikipedia_content, "blue"))
    print("Finally, although not intended for human consumption, all responses from the OSM server has been "
          "cached here: " + colored(osm.osm_responses_file, "blue"))


def write_header_to_file(file_name):
    with open(file_name, 'w') as outfile:
        outfile.write(
            u"'''Vad är denna sida?''' Detta är en delmängd av de gator etc. som finns listade på " +
            u"[[Gatunamn i Göteborg från och med 2001]]. De namn som finns i listan på denna sida är " +
            u"sådana som för närvarande saknas på [[Open Street Map]]. Syftet är alltså att få en " +
            u"överblick över namn som saknas på Open Street Map i Göteborgsområdet. Man kan, i rutan " +
            u"till höger om innehållsförteckningen, få en karta ritad, med alla namn till vilka det " +
            u"finns koordinater.\n\nDenna sida är automatiskt genererad från " +
            u"[https://github.com/sjoblomj/wikipedia_streetname_filter ett skript]\n\n----\n\n")


wikipedia_page_2001_to_2016 = wikipedia.download_page_2001_to_2016()
wikipedia_page_2017_to_now  = wikipedia.download_page_2017_to_now()
write_header_to_file(missing_features_file)

ioutils.write_to_file(missing_features_file, wikipedia.get_header(wikipedia_page_2001_to_2016))
ioutils.write_to_file(updated_wikipedia_content, wikipedia.get_header(wikipedia_page_2001_to_2016), "w")

json_wp_data = ioutils.read_json_string(wikipedia.content_to_json(wikipedia.get_content(wikipedia_page_2001_to_2016))) +\
               ioutils.read_json_string(wikipedia.content_to_json(wikipedia.get_content(wikipedia_page_2017_to_now)))

get_missing_features(json_wp_data)

ioutils.write_to_file(missing_features_file, wikipedia.remove_categories(wikipedia.get_footer(wikipedia_page_2001_to_2016)))
ioutils.write_to_file(updated_wikipedia_content, wikipedia.get_footer(wikipedia_page_2001_to_2016))

ioutils.write_to_file(osm.osm_responses_file, json.dumps(osm.cached_osm_responses), "w")
