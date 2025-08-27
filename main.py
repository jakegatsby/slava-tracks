import json
import logging
import os

from typing import Annotated

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

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("index.html")


#@app.post("/tracks/")
#async def create_track(track_title: Annotated[str, Form()], artist: Annotated[str, Form()], streaming_link: Annotated[str, Form()], styles:  Annotated[str, Form()]):
#    print("FOO")


@app.post("/tracks/")
async def create_track(request: Request):
    try:
        data = await request.json()
        print(data)
    except Exception as e:
        print(e)

