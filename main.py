from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import date
from glob import glob

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

templates = Jinja2Templates(directory="templates")

YEAR = 2022
DEC = 12
FIRST_DAY = date(year=YEAR, month=DEC, day=1)
LAST_PUBLIC_DAY = date(year=YEAR, month=DEC, day=31)
LAST_CONTENT_DAY = date(year=YEAR, month=DEC, day=31)
ASSET_PATH = Path(Path.cwd(), 'assets')
TYPES = [
    'simpsons'
]


def get_today() -> int:
    """Returning todays date, or -1 of out of bounds
        :returns
        0: too early
        -1: absolutely too late
        25: last content show latest
        1:24: show content of that day, being between 1 and 24 of december
    """
    today = date.today()
    if today < FIRST_DAY:
        return 0
    if today > LAST_PUBLIC_DAY:
        return -1
    if today > LAST_CONTENT_DAY:
        return 25
    return today.day


def get_today_debug() -> int:
    """This is for testing and jinja debugging only"""
    return 1


def get_test_from_assets(day: str, requested_type: str) -> str:
    """load quote to test and return"""
    with Path(ASSET_PATH, requested_type, day, 'quote.txt').open('r') as quote_fp:
        text = quote_fp.read()
    return text.lstrip()


def get_image_path_from_assets(day: str, requested_type: str) -> str:
    """glob the image path for today
        day string is expected to be preformated with leading zero
    """
    [image_file] = glob(str(Path(Path.cwd(), 'assets', requested_type, day, 'image*')))
    image_file_name = Path(image_file).name
    return f"/assets/{requested_type}/{day}/{image_file_name}"


@app.get("/", response_class=RedirectResponse)
async def root():
    """redirect to latest simpsons content"""
    return RedirectResponse(url='/simpsons')


@app.get("/{requested_type}", response_class=HTMLResponse)
async def return_entry(request: Request, requested_type: str):
    """Default: call template of that type"""
    if requested_type not in TYPES:
        return HTTPException(status_code=404,
                             detail=f"Type not found, available types are {', '.join(TYPES)}")
    todays_day = get_today()
    today_string = f"{todays_day:02d}"

    return templates.TemplateResponse("index.html",
                                      context={"request": request,
                                               "type": requested_type.title(),
                                               "day": today_string,
                                               "quote":
                                                   get_test_from_assets(today_string,
                                                                        requested_type),
                                               "image":
                                                   get_image_path_from_assets(today_string,
                                                                              requested_type)
                                               })


@app.get("/{requested_type}/{day}", response_class=HTMLResponse)
async def return_day_entry(request: Request, requested_type: str, day: int):
    """check day, must not
        - larger than todays_day
        - past last public day
    """
    if requested_type not in TYPES:
        return HTTPException(status_code=404,
                             detail=f"Type not found, available types are {', '.join(TYPES)}")
    todays_day = get_today()
    if todays_day >= day:
        today_string = f"{day:02d}"
        return templates.TemplateResponse("index.html",
                                          context={"request": request,
                                                   "type": requested_type.title(),
                                                   "day": today_string,
                                                   "quote":
                                                       get_test_from_assets(today_string,
                                                                            requested_type),
                                                   "image":
                                                       get_image_path_from_assets(today_string,
                                                                                  requested_type)
                                                   })
    if todays_day == -1:
        return {"message": "too late bro"}
    return RedirectResponse(url=f"/{requested_type}")
