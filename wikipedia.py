#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import requests


wikipedia_url_2001_to_2016 = "http://sv.wikipedia.org/w/index.php?action=raw&title=Gatunamn_i_G%C3%B6teborg_fr%C3%A5n_och_med_2001"
wikipedia_url_2017_to_now  = "http://sv.wikipedia.org/w/index.php?action=raw&title=Gatunamn_i_G%C3%B6teborg_fr%C3%A5n_och_med_2001/2017"
valid_keys = [u"gatunamn", u"stadsdel", u"motivering", u"typ", u"fastställd", u"koordinater", u"bild",
              u"fotnot-namn", u"fotnot"]


def remove_links(name):
    if name.find("|") == -1:
        return name.replace("[[", "").replace("]]", "")
    else:
        name = re.sub(r".*\|", "", name)
        return name.replace("]]", "")


def download_page_2001_to_2016():
    return requests.get(wikipedia_url_2001_to_2016).text

def download_page_2017_to_now():
    return requests.get(wikipedia_url_2017_to_now) .text


def get_header(page):
    template = "{{Gatulista-huvud}}"
    return page.split(template)[0] + template


def get_footer(page):
    template = "|}"
    return template + page.split(template)[1]


def get_content(page):
    return page.replace(get_header(page), "").replace(get_footer(page), "")


def remove_categories(page):
    return re.sub(r"\n\[\[Kategori:(.*)", "", page)


def content_to_json(content):
    content = re.sub("\"", "`", content)
    keys = "|".join(valid_keys)
    p = re.compile(r"\|[ \t]*(" + keys + r")[ \t]*=[ \t]*(.*)\n")
    new_content = p.sub('  \"\\1\": \"\\2\",\n', content)
    new_content = re.sub("\n{{Gatulista", "\n{", new_content)
    new_content = re.sub("\n}}\n", "\n},\n", new_content)
    new_content = re.sub(",\n}", "\n}", new_content)
    return "[\n" + new_content[0:len(new_content) - 2] + "\n]\n"


def align_key(key):
    longest_key = len(max(valid_keys, key=(lambda x: len(x))))
    length = longest_key - len(key)
    return (u" " * length)[:length]


def format_output_line(data, key):
    val = re.sub("`", "\"", data[key])
    return u"".join(("| ", key, align_key(key), " = ", val))


def print_json_to_file(file_name, data):
    with open(file_name, 'a') as outfile:
        outfile.write("{{Gatulista\n")
        for key in valid_keys:
            if key not in data:
                continue
            outfile.write(format_output_line(data, key))
            outfile.write("\n")
        outfile.write("}}\n")
