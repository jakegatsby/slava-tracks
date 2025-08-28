import json
import logging
import os

from datetime import datetime
from typing import Annotated

from psycopg.errors import UniqueViolation
from flask import Flask, render_template, send_file, request, jsonify
from sqlalchemy import create_engine, MetaData, Table, Column, Boolean, DateTime, Integer, String, select, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

try:
    DATABASE_URL = os.environ["DATABASE_URL"]
    logger.info("Got DATABASE_URL")
except KeyError:
    logger.error("Unable to get DATABASE_URL")

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

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

class Track(Base):
    __tablename__ = 'tracks'
    __table_args__ = (
        UniqueConstraint('title', 'artist', name='_title_artist_uc'),
    )
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
        return ", ".join(styles)


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
    return jsonify(sorted([t.to_dict() for t in session.query(Track).all()], key=lambda x: x["timestamp"]))

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return send_file('templates/index.html')  # no .j2 extension, so no jinja rendering here

    @app.route("/tracks/")
    def get_tracks():
        with Session.begin() as session:
            return tracks_to_json(session)

    @app.route("/tracks/", methods=["POST"])
    def add_track():
        data = request.json
        data.update({'timestamp': datetime.now()})
        track = Track(**data)
        with Session.begin() as session:
            session.add(track)
            return tracks_to_json(session)

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, IntegrityError):
            if isinstance(e.orig, UniqueViolation):
                if "_title_artist_uc" in str(e.orig):
                    return {
                        "error": "UniqueViolation _title_artist_uc"
                    }

    return app

