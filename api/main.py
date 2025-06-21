from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from pytz import timezone, country_timezones, all_timezones
import maxminddb

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="static")

db = maxminddb.open_database("2025-05-26-GeoOpen-Country.mmdb")

def get_country(ip: str) -> str | None:
    try:
        country = db.get(ip)
        if country and "country" in country:
            return country["country"]["iso_code"]
        return None
    except Exception as e:
        print(f"Error retrieving country for IP {ip}: {e}")
        return None


@app.get("/", response_class=HTMLResponse)
async def showtime(request: Request, tz: str | None = None, reset: bool = False):
    # Get client's IP address
    client = request.client.host
    country = country = get_country(client)
    clientTimezone = tz
    
	# If reset is set to true, clear all the search parameters
    if reset:
        return RedirectResponse(url="/")

	# If timezone is provided through the search parameters, try to use it
    if tz != None:
        print(f"Timezone provided: {tz}")
        try:
            timezone(tz)
        except Exception as e:
            print(f"Invalid timezone {tz}: {e}")
            return RedirectResponse(url="/")
    else:
        clientTimezone = country_timezones.get(country, ["UTC"])[0]

    print(f"Client IP: {client}, Country: {country}, Timezone: {clientTimezone}")

    currenttime = datetime.now(timezone(clientTimezone))
    
    secondHandDelay = currenttime.second
    minuteHandDelay = currenttime.minute * 60
    hourHandDelay = (currenttime.hour % 12) * 3600 + minuteHandDelay

    print(secondHandDelay, minuteHandDelay, hourHandDelay)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "timezones": all_timezones,
            "selected": clientTimezone,
            "secondHandDelay": secondHandDelay,
            "minuteHandDelay": minuteHandDelay,
            "hourHandDelay": hourHandDelay,
        },
    )