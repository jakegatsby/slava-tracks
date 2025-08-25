import json

from typing import Annotated

from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import FileResponse
from fastapi.responses import JSONResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("index.html")


@app.get("/styles/")
async def read_index():
    return STYLES


#@app.post("/tracks/")
#async def create_track(track_title: Annotated[str, Form()], artist: Annotated[str, Form()], streaming_link: Annotated[str, Form()], styles:  Annotated[str, Form()]):
#    print("FOO")


@app.post("/tracks/")
async def create_track(request: Request):
    print("FOO")

