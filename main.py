from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from datetime import date

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
templates = Jinja2Templates(directory="templates")

YEAR = 2022
DEC = 12
FIRST_DAY = date(year=YEAR, month=DEC, day=1)
LAST_PUBLIC_DAY = date(year=YEAR, month=DEC, day=31)
LAST_CONTENT_DAY = date(year=YEAR, month=DEC, day=31)

TYPES = [
    'simpsons'
]


def get_today() -> int:
    """Returning todays date, or -1 of out of bounds
        :returns
        -1: too early
        -2: absolutely too late
        25: last content show latest
        1:24: show content of that day, being between 1 and 24 of december
    """
    today = date.today()
    if today < FIRST_DAY:
        return -1
    if today > LAST_PUBLIC_DAY:
        return -2
    if today > LAST_CONTENT_DAY:
        return 25
    return today.day


@app.get("/", response_class=RedirectResponse)
async def root():
    """redirect to latest simpsons content"""
    return RedirectResponse(url='/simpsons')


@app.get("/{type}", response_class=HTMLResponse)
async def return_entry(request: Request, requested_type: str):
    """Default: call template of that type"""
    if requested_type not in TYPES:
        return HTTPException(status_code=404,
                             detail=f"Type not found, available types are {', '.join(TYPES)}")
    todays_day = get_today()
    if todays_day in range(1, 25):
        return templates.TemplateResponse("item.html",
                                          {"request": request, "day": todays_day,
                                           "type": requested_type})
    return {"message": "out of range"}


@app.get("/{type}/{day}", response_class=HTMLResponse)
async def say_hello(request: Request, requested_type: str, day: int):
    """check day, must not
        - larger than todays_day
        - past last public day
    """
    if requested_type not in TYPES:
        return HTTPException(status_code=404,
                             detail=f"Type not found, available types are {', '.join(TYPES)}")
    todays_day = get_today()
    if todays_day > day:
        return templates.TemplateResponse("item.html",
                                          {"request": request, "day": day,
                                           "type": requested_type})
    if todays_day == -2:
        return {"message": "too late bro"}
    return RedirectResponse(url=f"/{requested_type}")
