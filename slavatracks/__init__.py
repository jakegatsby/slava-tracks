import json
import logging
import os

from datetime import datetime
from typing import Annotated

from flask import Flask, render_template, send_file, request, jsonify
from sqlalchemy import create_engine, MetaData, Table, Column, Boolean, DateTime, Integer, String, select
from sqlalchemy.orm import sessionmaker, declarative_base


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

class Track(Base):
    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    artist = Column(String)
    streaming_link = Column(String)
    timestamp = Column(DateTime)
    argentine_tango = Column(Boolean)
    bachata = Column(Boolean)
    bolero = Column(Boolean)
    cha_cha = Column(Boolean)
    east_coast_swing = Column(Boolean)
    foxtrot = Column(Boolean)
    hustle = Column(Boolean)
    jive = Column(Boolean)
    lindy_hop = Column(Boolean)
    mambo = Column(Boolean)
    merengue = Column(Boolean)
    night_club_2_step = Column(Boolean)
    paso_doble = Column(Boolean)
    peabody = Column(Boolean)
    quickstep = Column(Boolean)
    rumba = Column(Boolean)
    salsa = Column(Boolean)
    samba = Column(Boolean)
    tango = Column(Boolean)
    viennese_waltz = Column(Boolean)
    waltz = Column(Boolean)
    west_coast_swing = Column(Boolean)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "streaming_link": self.streaming_link,
            "timestamp": str(self.timestamp),
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

def tracks_to_json():
    with Session.begin() as session:
        return jsonify(sorted([t.to_dict() for t in session.query(Track).all()], key=lambda x: x["timestamp"]))

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return send_file('templates/index.html')  # no .j2 extension, so no jinja rendering here

    @app.route("/tracks/")
    def get_tracks():
        with Session.begin() as session:
            return tracks_to_json()

    @app.route("/tracks/", methods=["POST"])
    def add_track():
        data = request.json
        data.update({'timestamp': datetime.now()})
        track = Track(**data)
        with Session.begin() as session:
            session.add(track)
            return tracks_to_json()

    return app

