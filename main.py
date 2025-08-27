import json
import logging
import os

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, MetaData, Table, Column, Boolean, Integer, String, select
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import FileResponse
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

try:
    DATABASE_URL = os.environ["DATABASE_URL"]
    logger.info("Got DATABASE_URL")
except KeyError:
    logger.error("Unable to get DATABASE_URL")

ENGINE = create_engine(DATABASE_URL)
Session = sessionmaker(ENGINE)
METADATA = MetaData()

class TracksSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    artist: str
    streaming_link: str
    description: str = ""
    timestamp: datetime
    argentine_tango: bool = False
    bachata: bool = False
    bolero: bool = False
    cha_cha: bool = False
    east_coast_swing: bool = False
    foxtrot: bool = False
    hustle: bool = False
    jive: bool = False
    lindy_hop: bool = False
    mambo: bool = False
    merengue: bool = False
    night_club_2_step: bool = False
    paso_doble: bool = False
    peabody: bool = False
    quickstep: bool = False
    rumba: bool = False
    salsa: bool = False
    samba: bool = False
    tango: bool = False
    viennese_waltz: bool = False
    waltz: bool = False
    west_coast_swing: bool = False


TRACKS_TABLE = Table(
    'tracks', METADATA,
    Column('id', Integer, primary_key=True),
    Column('title', String),
    Column('artist', String),
    Column('streaming_link', String),
    Column('argentine_tango', Boolean),
    Column('bachata', Boolean),
    Column('bolero', Boolean),
    Column('cha_cha', Boolean),
    Column('east_coast_swing', Boolean),
    Column('foxtrot', Boolean),
    Column('hustle', Boolean),
    Column('jive', Boolean),
    Column('lindy_hop', Boolean),
    Column('mambo', Boolean),
    Column('merengue', Boolean),
    Column('night_club_2_step', Boolean),
    Column('paso_doble', Boolean),
    Column('peabody', Boolean),
    Column('quickstep', Boolean),
    Column('rumba', Boolean),
    Column('salsa', Boolean),
    Column('samba', Boolean),
    Column('tango', Boolean),
    Column('viennese_waltz', Boolean),
    Column('waltz', Boolean),
    Column('west_coast_swing', Boolean),
)

METADATA.create_all(ENGINE, checkfirst=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("index.html")


@app.get("/tracks/")
async def get_tracks():
    rows = []
    with Session.begin() as session:
        import pdb; pdb.set_trace()


@app.post("/tracks/")
async def create_track(request: Request):
    try:
        data = await request.json()
        print(data)
    except Exception as e:
        print(e)

