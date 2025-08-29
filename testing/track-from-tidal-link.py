#!/usr/bin/env python

import re

import requests
from bs4 import BeautifulSoup


def get_track_info(url):
    tidal_page = requests.get(url)
    soup = BeautifulSoup(tidal_page.content, "html.parser")

    for title in soup.find_all("title"):
        title = title.string
        if title.endswith("| Spotify"):
            match = re.search(r"^(.*) - song and lyrics by (.*) \| Spotify", title)
            print(match.groups())




#get_track_info("https://tidal.com/browse/track/370686004?u")
get_track_info("https://open.spotify.com/track/53o05J0uSWOedPwN4Z0oyo?si=XGAiSUelTOW6HTmHFkWn-A")