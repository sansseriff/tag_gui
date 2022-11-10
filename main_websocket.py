import json
import uvicorn
import asyncio
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi import WebSocket


# from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel


from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException  # for the basic endpoint


from fastapi import Query
from fastapi import Body


from datetime import timedelta, datetime


class Looper:
    def __init__(self, ls):
        self.ls = ls

    def __iter__(self):
        self.num = 0
        self.max = len(self.ls)
        return self

    def __next__(self):
        if self.num >= self.max:
            self.num = 0
        val = self.ls[self.num]
        self.num += 1
        return val


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# connect(db="hrms", host="localhost", port=27017)
# # templates = Jinja2Templates(directory="templates")


with open("measurements.json", "r") as file:
    loop = Looper(json.loads(file.read()))
    measurements = iter(loop)


app.mount("/t", StaticFiles(directory="static"), name="static")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await asyncio.sleep(round(1 / 60, 3))
        payload = next(measurements)
        print(payload)
        await websocket.send_json(payload)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # , reload=True, debug=True)
