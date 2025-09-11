import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from statistics import mode
from typing import Annotated
from urllib.parse import urlparse

import requests
import spotipy
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request, send_file
from psycopg.errors import UniqueViolation
from spotipy.oauth2 import SpotifyClientCredentials
from sqlalchemy import (Boolean, Column, DateTime, Integer, MetaData, String,
                        Table, UniqueConstraint, create_engine, select)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

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
        share_url = Column(String)
        timestamp = Column(DateTime)
        tidal_url = Column(String, default=None)
        spotify_url = Column(String, default=None)
        youtube_url = Column(String, default=None)
        apple_music_url = Column(String, default=None)
        itunes_url = Column(String, default=None)
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
                "timestamp": str(self.timestamp),
                "timestamp_day": str(self.timestamp).split()[0],
                "share_url": self.share_url,
                "tidal_url": self.tidal_url,
                "spotify_url": self.spotify_url,
                "youtube_url": self.youtube_url,
                "apple_music_url": self.apple_music_url,
                "itunes_url": self.itunes_url,
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


def track_from_request_data(data):
    params = {"url": data["share_url"], "userCountry": "CA", "songIfSingle": "true"}
    r = requests.get("https://api.song.link/v1-alpha.1/links", params=params)
    titles = []
    artists = []
    track = Track(**data)
    for platform, track_data in r.json()["entitiesByUniqueId"].items():
        titles.append(track_data["title"])
        artists.append(track_data["artistName"])
    track.title = mode(titles)
    track.artist = mode(artists)
    for platform, track_data in r.json()["linksByPlatform"].items():
        if platform == "tidal":
            track.tidal_url = track_data["url"]
        elif platform == "spotify":
            track.spotify_url = track_data["url"]
        elif platform == "youtube":
            track.youtube_url = track_data["url"]
    track.timestamp = datetime.now()
    return track


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
        logger.info(f"Request Data: {data}")
        track = track_from_request_data(data)
        with Session.begin() as session:
            session.add(track)
            logger.info(f"Added {track.to_dict()}")
            return tracks_to_json(session)

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(e)
        if isinstance(e, IntegrityError):
            if isinstance(e.orig, UniqueViolation):
                if "_title_artist_uc" in str(e.orig):
                    return {"error": "This track has already been added"}
        # elif isinstance(e, StreamingPlatformNotSupported):  # FIXME - replace with can't find song.link ????
        #    return {"error": "This streaming platform URL is not supported"}

    return app
