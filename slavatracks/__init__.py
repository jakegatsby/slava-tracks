import json
import logging
import os
import re
from datetime import datetime
from typing import Annotated

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request, send_file
from psycopg.errors import UniqueViolation
from sqlalchemy import (Boolean, Column, DateTime, Integer, MetaData, String,
                        Table, UniqueConstraint, create_engine, select)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def get_track_info_from_url(url):
    if url.casefold().startswith("https://tidal.com"):
        return get_tidal_track_info(url)
    elif url.casefold().startswith("https://open.spotify.com"):
        return get_spotify_track_info(url)
    else:
        return None, None, None


def get_tidal_track_info(url):
    track_match = re.search(r".*track/([0-9]*).*", url)
    if not track_match:
        return None, None, None
    track_id = track_match.groups()[0]
    url = f"https://tidal.com/browse/track/{track_id}/u"
    logger.info(f"Parsing TIDAL URL: {url}")
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    for meta in soup.find_all("meta"):
        content = meta.get("content")
        if not content:
            continue
        match = re.search(
            r"^Listen to (.*), a song by (.*) on .*$",
            content,
        )
        if match:
            return url, match.groups()[0], match.groups()[1]

    logger.debug(str(soup)))
    logger.error(f"Unable to parse {url}")
    return url, None, None


def get_spotify_track_info(url):
    logger.info(f"Parsing SPOTIFY URL: {url}")
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    for title in soup.find_all("title"):
        title = title.string
        if title.endswith("| Spotify"):
            match = re.search(r"^(.*) - song and lyrics by (.*) \| Spotify", title)
            if match:
                return url, match.groups()[0], match.groups()[1]
    logger.error(f"Unable to parse {url}")
    return None, None, None


STYLE_ATTRS = [
    "argentine_tango",
    "bachata",
    "bolero",
    "cha_cha",
    "east_coast_swing",
    "foxtrot",
    "hustle",
    "jive",
    "lindy_hop",
    "mambo",
    "merengue",
    "night_club_2_step",
    "paso_doble",
    "peabody",
    "quickstep",
    "rumba",
    "salsa",
    "samba",
    "tango",
    "viennese_waltz",
    "waltz",
    "west_coast_swing",
]


def style_attr_to_checkbox(s):
    s = s.replace("_", " ").title().replace(" ", "") + "Checkbox"
    return s[0].lower() + s[1:]


def style_attr_to_input_name(s):
    return s.replace("_", "-")


def style_attr_to_title(s):
    return s.replace("_", " ").title()


def style_attr_to_details_li(s):
    return f'<li><label><input type="checkbox" v-model="{style_attr_to_checkbox(s)}" name="{style_attr_to_input_name(s)}" />{style_attr_to_title(s)}</label></li><li>'


try:
    DATABASE_URL = os.environ["DATABASE_URL"]
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
    logger.info("DATABASE_URL modified for psycopg-3")
except KeyError:
    logger.error("Unable to get DATABASE_URL")
    DATABASE_URL = None

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)

    class Track(Base):
        __tablename__ = "tracks"
        __table_args__ = (UniqueConstraint("title", "artist", name="_title_artist_uc"),)
        id = Column(Integer, primary_key=True)
        title = Column(String)
        artist = Column(String)
        streaming_link = Column(String)
        timestamp = Column(DateTime)
        argentine_tango = Column(Boolean, default=False)
        bachata = Column(Boolean, default=False)
        bolero = Column(Boolean, default=False)
        cha_cha = Column(Boolean, default=False)
        east_coast_swing = Column(Boolean, default=False)
        foxtrot = Column(Boolean, default=False)
        hustle = Column(Boolean, default=False)
        jive = Column(Boolean, default=False)
        lindy_hop = Column(Boolean, default=False)
        mambo = Column(Boolean, default=False)
        merengue = Column(Boolean, default=False)
        night_club_2_step = Column(Boolean, default=False)
        paso_doble = Column(Boolean, default=False)
        peabody = Column(Boolean, default=False)
        quickstep = Column(Boolean, default=False)
        rumba = Column(Boolean, default=False)
        salsa = Column(Boolean, default=False)
        samba = Column(Boolean, default=False)
        tango = Column(Boolean, default=False)
        viennese_waltz = Column(Boolean, default=False)
        waltz = Column(Boolean, default=False)
        west_coast_swing = Column(Boolean, default=False)

        def prettified_styles(self):
            styles = []
            for a in sorted(self.__dict__.keys()):
                if a in STYLE_ATTRS:
                    if self.__dict__[a]:
                        styles.append(a.replace("_", " ").title())
            prettified = ", ".join(styles)
            return prettified

        def to_dict(self):
            return {
                "id": self.id,
                "title": self.title,
                "artist": self.artist,
                "streaming_link": self.streaming_link,
                "timestamp": str(self.timestamp),
                "prettified_styles": self.prettified_styles(),
                "argentine_tango": bool(self.argentine_tango),
                "bachata": bool(self.bachata),
                "bolero": bool(self.bolero),
                "cha_cha": bool(self.cha_cha),
                "east_coast_swing": bool(self.east_coast_swing),
                "foxtrot": bool(self.foxtrot),
                "hustle": bool(self.hustle),
                "jive": bool(self.jive),
                "lindy_hop": bool(self.lindy_hop),
                "mambo": bool(self.mambo),
                "merengue": bool(self.merengue),
                "night_club_2_step": bool(self.night_club_2_step),
                "paso_doble": bool(self.paso_doble),
                "peabody": bool(self.peabody),
                "quickstep": bool(self.quickstep),
                "rumba": bool(self.rumba),
                "salsa": bool(self.salsa),
                "samba": bool(self.samba),
                "tango": bool(self.tango),
                "viennese_waltz": bool(self.viennese_waltz),
                "waltz": bool(self.waltz),
                "west_coast_swing": bool(self.west_coast_swing),
            }

    Base.metadata.create_all(engine, checkfirst=True)


def tracks_to_json(session):
    return jsonify(
        sorted(
            [t.to_dict() for t in session.query(Track).all()],
            key=lambda x: x["timestamp"],
            reverse=True,
        )
    )


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return send_file(
            "templates/index.html"
        )  # no .j2 extension, so no jinja rendering here

    @app.route("/favicon.ico")
    def favicon():
        return send_file("static/favicon.ico")

    @app.route("/tracks/")
    def get_tracks():
        with Session.begin() as session:
            return tracks_to_json(session)

    @app.route("/tracks/", methods=["POST"])
    def add_track():
        data = request.json
        url, title, artist = get_track_info_from_url(data["streaming_link"])
        if not title:
            return {"error": f"[ERROR] Could not determine track info from {data['streaming_link']}"}
        data.update({"streaming_link": url, "title": title, "artist": artist, "timestamp": datetime.now()})
        track = Track(**data)
        with Session.begin() as session:
            session.add(track)
            logger.info(f"Added {track.to_dict()}")
            return tracks_to_json(session)

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, IntegrityError):
            if isinstance(e.orig, UniqueViolation):
                if "_title_artist_uc" in str(e.orig):
                    return {"error": "[ERROR] This track has already been added"}

    return app
