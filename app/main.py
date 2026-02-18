from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import pytz
import httpx
import json
import logging
from typing import Optional, Dict, Any, List
from app.data.cities import COUNTRIES_AND_CITIES, TIMEZONES, FIQH_METHODS, get_timezone_for_coordinates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ramadan Countdown API",
    description="Dynamic Ramadan countdown for Sehri and Iftar times with auto-detection",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Simple in-memory cache
prayer_time_cache: Dict[str, Any] = {}

# Debug mode flag
DEBUG_MODE = True

def get_cache_key(lat: float, lon: float, date: str, method: int, school: int) -> str:
    """Generate cache key for prayer times"""
    return f"{lat},{lon},{date},{method},{school}"

def convert_to_12_hour(time_24: str) -> str:
    """Convert 24-hour time to 12-hour format"""
    if not time_24:
        return "--:--"
    try:
        parts = time_24.split(':')
        hours = int(parts[0])
        minutes = parts[1] if len(parts) > 1 else "00"
        am_pm = "AM" if hours < 12 else "PM"
        hours_12 = hours if hours <= 12 else hours - 12
        if hours_12 == 0:
            hours_12 = 12
        return f"{hours_12}:{minutes} {am_pm}"
    except:
        return time_24

def parse_time_to_datetime(time_str: str, date_str: str, timezone_str: str) -> Optional[datetime]:
    """
    Parse a time string (HH:MM) into a datetime object in the specified timezone.
    
    Args:
        time_str: Time in HH:MM format
        date_str: Date in DD-MM-YYYY format
        timezone_str: Timezone string (e.g., "Asia/Karachi")
    
    Returns:
        datetime object in the specified timezone or None if parsing fails
    """
    try:
        tz = pytz.timezone(timezone_str)
        day, month, year = map(int, date_str.split('-'))
        hours, minutes = map(int, time_str.split(':'))
        
        dt = datetime(year, month, day, hours, minutes, 0)
        return tz.localize(dt)
    except Exception as e:
        logger.error(f"Error parsing time: {e}")
        return None

def calculate_countdown(target_time: datetime, current_time: datetime) -> Dict[str, int]:
    """
    Calculate countdown between current time and target time.
    Pure function - no side effects.
    
    Args:
        target_time: Target datetime (timezone-aware)
        current_time: Current datetime (timezone-aware, same timezone)
    
    Returns:
        Dictionary with hours, minutes, seconds remaining
    """
    if target_time <= current_time:
        # Target has passed, calculate for next day
        target_time += timedelta(days=1)
    
    diff = target_time - current_time
    total_seconds = int(diff.total_seconds())
    
    if total_seconds < 0:
        total_seconds = 0
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return {
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "total_seconds": total_seconds
    }

async def fetch_prayer_times(
    lat: float, 
    lon: float, 
    date: str, 
    timezone: str, 
    fiqh_method: str,
    debug: bool = False
) -> Dict[str, Any]:
    """
    Fetch prayer times from AlAdhan API.
    
    AlAdhan API Parameters:
    - method: Calculation method
      - 0 = Shia Ithna-Ashari, Leva Institute, Qum (Jafari)
      - 1 = University of Islamic Sciences, Karachi
      - 2 = Islamic Society of North America (ISNA)
      - 3 = Muslim World League
      - 4 = Umm Al-Qura University, Makkah
      - 5 = Egyptian General Authority of Survey
      - 7 = Institute of Geophysics, University of Tehran
      - 8 = Gulf Region
      - 9 = Kuwait
      - 10 = Qatar
      - 11 = Majlis Ugama Islam Singapura, Singapore
      - 12 = Union Organization islamic de France
      - 13 = Diyanet İşleri Başkanlığı, Turkey
      - 14 = Spiritual Administration of Muslims of Russia
    
    - school: Madhab (for Asr calculation)
      - 0 = Shafi, Maliki, Hanbali (standard)
      - 1 = Hanafi
    
    Sehri (Ends at Fajr):
    - Use Fajr time directly from API
    - No arbitrary subtraction
    
    Iftar (At Maghrib):
    - Use Maghrib time directly from API
    - No manual offsets
    """
    
    # Determine calculation method and school based on fiqh
    # For Jafari (Shia): method=0 (Jafari method), school doesn't matter for Asr
    # For Hanafi: method=1 (Karachi), school=1 (Hanafi Asr)
    # For Shafi/Maliki/Hanbali: method=1 (Karachi), school=0 (Shafi Asr)
    
    if fiqh_method == "jaffari":
        # Jafari (Shia) method - uses Leva Institute calculations
        method = 0  # Shia Ithna-Ashari, Leva Institute, Qum
        school = 0  # School doesn't affect Jafari method
    elif fiqh_method == "hanafi":
        # Hanafi method - uses Karachi calculations with Hanafi Asr
        method = 1  # University of Islamic Sciences, Karachi
        school = 1  # Hanafi school for Asr
    else:
        # Shafi/Maliki/Hanbali - uses Karachi calculations with Shafi Asr
        method = 1  # University of Islamic Sciences, Karachi
        school = 0  # Shafi school for Asr
    
    cache_key = get_cache_key(lat, lon, date, method, school)
    
    # Check cache
    if cache_key in prayer_time_cache:
        cached_data = prayer_time_cache[cache_key]
        if cached_data.get("date") == date:
            logger.info(f"Using cached prayer times for {cache_key}")
            return cached_data
    
    url = "https://api.aladhan.com/v1/timings"
    params = {
        "latitude": lat,
        "longitude": lon,
        "method": method,
        "school": school,
        "date": date,
        "timezone": timezone
    }
    
    # Log API request parameters for debugging
    logger.info(f"AlAdhan API Request - URL: {url}")
    logger.info(f"AlAdhan API Request - Params: lat={lat}, lon={lon}, method={method}, school={school}, date={date}, timezone={timezone}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("code") == 200:
                    timings = data.get("data", {}).get("timings", {})
                    date_info = data.get("data", {}).get("date", {})
                    meta = data.get("data", {}).get("meta", {})
                    
                    # Log raw API response for debugging
                    logger.info(f"AlAdhan API Response - Timings: {timings}")
                    logger.info(f"AlAdhan API Response - Meta: {meta}")
                    
                    # Sehri ends at Fajr - use directly from API
                    fajr_time = timings.get("Fajr", "")
                    # Iftar is at Maghrib - use directly from API
                    maghrib_time = timings.get("Maghrib", "")
                    
                    # Parse times to datetime for countdown calculations
                    fajr_dt = parse_time_to_datetime(fajr_time, date, timezone)
                    maghrib_dt = parse_time_to_datetime(maghrib_time, date, timezone)
                    
                    result = {
                        "date": date,
                        "timings": {
                            "Fajr": fajr_time,
                            "Sunrise": timings.get("Sunrise", ""),
                            "Dhuhr": timings.get("Dhuhr", ""),
                            "Asr": timings.get("Asr", ""),
                            "Maghrib": maghrib_time,
                            "Isha": timings.get("Isha", ""),
                        },
                        "timings_12h": {
                            "Fajr": convert_to_12_hour(fajr_time),
                            "Sunrise": convert_to_12_hour(timings.get("Sunrise", "")),
                            "Dhuhr": convert_to_12_hour(timings.get("Dhuhr", "")),
                            "Asr": convert_to_12_hour(timings.get("Asr", "")),
                            "Maghrib": convert_to_12_hour(maghrib_time),
                            "Isha": convert_to_12_hour(timings.get("Isha", "")),
                        },
                        "timezone": timezone,
                        "lat": lat,
                        "lon": lon,
                        "fiqh_method": fiqh_method,
                        "method": method,
                        "school": school,
                        "sehri_ends": fajr_time,
                        "sehri_ends_12h": convert_to_12_hour(fajr_time),
                        "iftar": maghrib_time,
                        "iftar_12h": convert_to_12_hour(maghrib_time),
                        "fajr_datetime": fajr_dt.isoformat() if fajr_dt else None,
                        "maghrib_datetime": maghrib_dt.isoformat() if maghrib_dt else None,
                    }
                    
                    # Add debug info if requested
                    if debug or DEBUG_MODE:
                        result["debug"] = {
                            "api_url": url,
                            "api_params": params,
                            "raw_timings": timings,
                            "meta": meta,
                            "fajr_parsed": fajr_dt.isoformat() if fajr_dt else None,
                            "maghrib_parsed": maghrib_dt.isoformat() if maghrib_dt else None,
                        }
                    
                    # Cache the result
                    prayer_time_cache[cache_key] = result
                    
                    return result
                else:
                    error_msg = data.get("data", "API returned error")
                    logger.error(f"AlAdhan API Error: {error_msg}")
                    raise HTTPException(status_code=400, detail=f"API returned error: {error_msg}")
            else:
                logger.error(f"AlAdhan API HTTP Error: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch prayer times: {response.status_code}")
                
    except httpx.RequestError as e:
        logger.error(f"AlAdhan API Request Error: {str(e)}")
        raise HTTPException(status_code=503, detail=f"API request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Internal Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

def find_closest_city(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Find the closest city from our database to the given coordinates"""
    if lat == 0 and lon == 0:
        return None
    
    min_distance = float('inf')
    closest = None
    
    for country, country_data in COUNTRIES_AND_CITIES.items():
        for city, city_data in country_data["cities"].items():
            city_lat = city_data["lat"]
            city_lon = city_data["lon"]
            
            # Calculate simple distance (not perfect but good enough)
            distance = ((lat - city_lat) ** 2 + (lon - city_lon) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest = {
                    "city": city,
                    "country": country,
                    "lat": city_lat,
                    "lon": city_lon,
                    "timezone": city_data["timezone"]
                }
    
    return closest

@app.get("/")
async def root():
    """Render the main page"""
    from fastapi.requests import Request
    return templates.TemplateResponse("index.html", {"request": {}})

@app.get("/api/detect-location")
async def detect_location(browser_timezone: Optional[str] = Query(None)):
    """Auto-detect user location based on browser timezone (fallback when geolocation is not available)"""
    browser_tz = browser_timezone or "UTC"
    
    # Try to find a city matching the browser timezone
    for country, country_data in COUNTRIES_AND_CITIES.items():
        for city, city_data in country_data["cities"].items():
            if city_data["timezone"] == browser_tz:
                return {
                    "detected": True,
                    "method": "timezone",
                    "detected_city": city,
                    "detected_country": country,
                    "detected_lat": city_data["lat"],
                    "detected_lon": city_data["lon"],
                    "detected_timezone": city_data["timezone"],
                    "browser_timezone": browser_tz,
                    "message": f"Location detected from timezone: {browser_tz}"
                }
    
    # Return default if no match found
    return {
        "detected": False,
        "method": "timezone",
        "detected_city": "Karachi",
        "detected_country": "Pakistan",
        "detected_lat": 24.8607,
        "detected_lon": 67.0011,
        "detected_timezone": "Asia/Karachi",
        "browser_timezone": browser_tz,
        "message": "Using default location"
    }

@app.get("/api/detect-location-from-coords")
async def detect_location_from_coords(
    lat: float = Query(...),
    lon: float = Query(...),
    browser_timezone: Optional[str] = Query(None)
):
    """Detect user location from browser-provided coordinates (from Geolocation API)"""
    # Find closest city from our database
    closest_city = find_closest_city(lat, lon)
    
    if closest_city:
        return {
            "detected": True,
            "method": "geolocation",
            "detected_city": closest_city["city"],
            "detected_country": closest_city["country"],
            "detected_lat": closest_city["lat"],
            "detected_lon": closest_city["lon"],
            "detected_timezone": closest_city["timezone"],
            "user_lat": lat,
            "user_lon": lon,
            "browser_timezone": browser_timezone,
            "message": f"Location detected from your device: {closest_city['city']}, {closest_city['country']}"
        }
    
    # Fallback to timezone-based detection
    browser_tz = browser_timezone or "UTC"
    for country, country_data in COUNTRIES_AND_CITIES.items():
        for city, city_data in country_data["cities"].items():
            if city_data["timezone"] == browser_tz:
                return {
                    "detected": True,
                    "method": "timezone_fallback",
                    "detected_city": city,
                    "detected_country": country,
                    "detected_lat": city_data["lat"],
                    "detected_lon": city_data["lon"],
                    "detected_timezone": city_data["timezone"],
                    "browser_timezone": browser_tz,
                    "message": f"Location detected from timezone: {browser_tz}"
                }
    
    # Return default if no match found
    return {
        "detected": False,
        "method": "default",
        "detected_city": "Karachi",
        "detected_country": "Pakistan",
        "detected_lat": 24.8607,
        "detected_lon": 67.0011,
        "detected_timezone": "Asia/Karachi",
        "browser_timezone": browser_tz,
        "message": "Using default location"
    }

@app.get("/api/countries")
async def get_countries():
    """Get list of available countries sorted alphabetically"""
    countries = sorted(list(COUNTRIES_AND_CITIES.keys()))
    return {"countries": countries}

@app.get("/api/cities/{country}")
async def get_cities(country: str):
    """Get cities for a specific country sorted alphabetically"""
    if country not in COUNTRIES_AND_CITIES:
        raise HTTPException(status_code=404, detail="Country not found")
    
    cities = sorted(list(COUNTRIES_AND_CITIES[country]["cities"].keys()))
    return {"cities": cities, "country": country}

@app.get("/api/city-data")
async def get_city_data(country: str = Query(...), city: str = Query(...)):
    """Get city coordinates and timezone"""
    if country not in COUNTRIES_AND_CITIES:
        raise HTTPException(status_code=404, detail="Country not found")
    
    if city not in COUNTRIES_AND_CITIES[country]["cities"]:
        raise HTTPException(status_code=404, detail="City not found")
    
    return COUNTRIES_AND_CITIES[country]["cities"][city]

@app.get("/api/timezones")
async def get_timezones():
    """Get list of available timezones sorted alphabetically"""
    return {"timezones": sorted(TIMEZONES)}

@app.get("/api/fiqh-methods")
async def get_fiqh_methods():
    """Get list of fiqh methods"""
    return {"methods": FIQH_METHODS}

@app.get("/api/prayer-times-all")
async def get_all_fiqh_prayer_times(
    country: str = Query(...),
    city: str = Query(...),
    date: Optional[str] = Query(None),
    timezone: Optional[str] = Query(None),
    format_12h: bool = Query(True),
    debug: bool = Query(False)
):
    """Get prayer times for all fiqh methods"""
    if country not in COUNTRIES_AND_CITIES:
        raise HTTPException(status_code=404, detail="Country not found")
    
    if city not in COUNTRIES_AND_CITIES[country]["cities"]:
        raise HTTPException(status_code=404, detail="City not found")
    
    city_data = COUNTRIES_AND_CITIES[country]["cities"][city]
    lat = city_data["lat"]
    lon = city_data["lon"]
    default_tz = city_data["timezone"]
    
    tz = timezone if timezone else default_tz
    
    # Get date
    if date is None:
        now = datetime.now(pytz.timezone(tz))
        date = now.strftime("%d-%m-%Y")
    else:
        try:
            datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Fetch times for all three methods
    results = {}
    for method in ["hanafi", "jaffari", "shafi"]:
        times = await fetch_prayer_times(lat, lon, date, tz, method, debug)
        iftar_time = times.get("iftar", times["timings"]["Maghrib"])
        iftar_12h = times.get("iftar_12h", convert_to_12_hour(iftar_time)) if format_12h else iftar_time
        
        results[method] = {
            "fiqh_method": method,
            "method_id": times.get("method"),
            "school_id": times.get("school"),
            "timings": times["timings"],
            "timings_12h": times.get("timings_12h", {}),
            "sehri_ends": times["timings"]["Fajr"],
            "sehri_ends_12h": convert_to_12_hour(times["timings"]["Fajr"]) if format_12h else times["timings"]["Fajr"],
            "iftar": iftar_time,
            "iftar_12h": iftar_12h,
            "fajr_datetime": times.get("fajr_datetime"),
            "maghrib_datetime": times.get("maghrib_datetime"),
        }
        
        if debug or DEBUG_MODE:
            results[method]["debug"] = times.get("debug")
    
    return {
        "country": country,
        "city": city,
        "date": date,
        "timezone": tz,
        "lat": lat,
        "lon": lon,
        "format_12h": format_12h,
        "fiqh_times": results
    }

@app.get("/api/prayer-times")
async def get_prayer_times(
    country: str = Query(...),
    city: str = Query(...),
    fiqh_method: str = Query("hanafi"),
    date: Optional[str] = Query(None),
    timezone: Optional[str] = Query(None),
    format_12h: bool = Query(True),
    debug: bool = Query(False)
):
    """Get prayer times for a specific city and date"""
    if country not in COUNTRIES_AND_CITIES:
        raise HTTPException(status_code=404, detail="Country not found")
    
    if city not in COUNTRIES_AND_CITIES[country]["cities"]:
        raise HTTPException(status_code=404, detail="City not found")
    
    city_data = COUNTRIES_AND_CITIES[country]["cities"][city]
    lat = city_data["lat"]
    lon = city_data["lon"]
    default_tz = city_data["timezone"]
    
    # Use provided timezone or default
    tz = timezone if timezone else default_tz
    
    # Get date (default to today)
    if date is None:
        now = datetime.now(pytz.timezone(tz))
        date = now.strftime("%d-%m-%Y")
    else:
        # Validate date format
        try:
            datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use DD-MM-YYYY")
    
    # Validate fiqh method
    if fiqh_method not in FIQH_METHODS:
        raise HTTPException(status_code=400, detail="Invalid fiqh method")
    
    # Fetch prayer times
    prayer_times = await fetch_prayer_times(lat, lon, date, tz, fiqh_method, debug)
    
    # Calculate Sehri and Iftar
    fajr = prayer_times["timings"]["Fajr"]
    maghrib = prayer_times["timings"]["Maghrib"]
    
    # Sehri ends at Fajr time
    sehri_end = fajr
    # Iftar is at Maghrib time  
    iftar = maghrib
    
    # Convert to 12-hour format if requested
    sehri_end_12h = convert_to_12_hour(sehri_end) if format_12h else sehri_end
    iftar_12h = convert_to_12_hour(iftar) if format_12h else iftar
    
    timings_12h = prayer_times.get("timings_12h", {}) if format_12h else prayer_times.get("timings", {})
    
    result = {
        "country": country,
        "city": city,
        "date": date,
        "timezone": tz,
        "lat": lat,
        "lon": lon,
        "fiqh_method": fiqh_method,
        "method": prayer_times.get("method"),
        "school": prayer_times.get("school"),
        "format_12h": format_12h,
        "coordinates": {"lat": lat, "lon": lon},
        "timings": prayer_times["timings"],
        "timings_12h": timings_12h,
        "sehri_ends": sehri_end,
        "sehri_ends_12h": sehri_end_12h,
        "iftar": iftar,
        "iftar_12h": iftar_12h,
        "fajr_datetime": prayer_times.get("fajr_datetime"),
        "maghrib_datetime": prayer_times.get("maghrib_datetime"),
    }
    
    if debug or DEBUG_MODE:
        result["debug"] = prayer_times.get("debug")
    
    return result

@app.get("/api/current-time")
async def get_current_time(timezone: Optional[str] = Query(None)):
    """Get current time in specified timezone"""
    if timezone is None:
        return {"current_time": datetime.now().isoformat(), "timezone": "UTC", "formatted_12h": datetime.now().strftime("%I:%M:%S %p")}
    
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return {
            "current_time": current_time.isoformat(),
            "timezone": timezone,
            "formatted": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "formatted_12h": current_time.strftime("%I:%M:%S %p"),
            "timestamp": current_time.timestamp()
        }
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail="Invalid timezone")

@app.get("/api/countdown")
async def get_countdown(
    country: str = Query(...),
    city: str = Query(...),
    fiqh_method: str = Query("hanafi"),
    timezone: Optional[str] = Query(None)
):
    """
    Get countdown to next Sehri or Iftar.
    Uses proper timezone handling for accurate countdown.
    """
    if country not in COUNTRIES_AND_CITIES:
        raise HTTPException(status_code=404, detail="Country not found")
    
    if city not in COUNTRIES_AND_CITIES[country]["cities"]:
        raise HTTPException(status_code=404, detail="City not found")
    
    city_data = COUNTRIES_AND_CITIES[country]["cities"][city]
    lat = city_data["lat"]
    lon = city_data["lon"]
    default_tz = city_data["timezone"]
    
    tz = timezone if timezone else default_tz
    
    # Get today's date in city timezone
    tz_obj = pytz.timezone(tz)
    now = datetime.now(tz_obj)
    date = now.strftime("%d-%m-%Y")
    
    # Fetch prayer times
    prayer_times = await fetch_prayer_times(lat, lon, date, tz, fiqh_method)
    
    fajr_time = prayer_times["timings"]["Fajr"]
    maghrib_time = prayer_times["timings"]["Maghrib"]
    
    # Parse times to datetime
    fajr_dt = parse_time_to_datetime(fajr_time, date, tz)
    maghrib_dt = parse_time_to_datetime(maghrib_time, date, tz)
    
    if not fajr_dt or not maghrib_dt:
        raise HTTPException(status_code=500, detail="Failed to parse prayer times")
    
    # Determine next event
    current_time = now
    
    # Check if we're before Fajr
    if current_time < fajr_dt:
        next_event = "sehri"
        target_time = fajr_dt
        event_name = "Sehri Ends (Fajr)"
    # Check if we're between Fajr and Maghrib
    elif current_time < maghrib_dt:
        next_event = "iftar"
        target_time = maghrib_dt
        event_name = "Iftar (Maghrib)"
    # After Maghrib, countdown to next day's Sehri
    else:
        next_event = "sehri"
        # Get tomorrow's Fajr
        tomorrow = now + timedelta(days=1)
        tomorrow_date = tomorrow.strftime("%d-%m-%Y")
        tomorrow_prayer = await fetch_prayer_times(lat, lon, tomorrow_date, tz, fiqh_method)
        tomorrow_fajr = tomorrow_prayer["timings"]["Fajr"]
        target_time = parse_time_to_datetime(tomorrow_fajr, tomorrow_date, tz)
        event_name = "Sehri Ends (Fajr)"
    
    # Calculate countdown
    countdown = calculate_countdown(target_time, current_time)
    
    return {
        "next_event": next_event,
        "event_name": event_name,
        "target_time": target_time.isoformat(),
        "target_time_12h": target_time.strftime("%I:%M %p"),
        "current_time": current_time.isoformat(),
        "current_time_12h": current_time.strftime("%I:%M:%S %p"),
        "countdown": countdown,
        "timezone": tz,
        "city": city,
        "country": country,
        "fiqh_method": fiqh_method
    }

@app.get("/api/search-city")
async def search_city(query: str = Query(...)):
    """Search for a city by name"""
    query_lower = query.lower()
    results = []
    
    for country, country_data in COUNTRIES_AND_CITIES.items():
        for city, city_data in country_data["cities"].items():
            if query_lower in city.lower():
                results.append({
                    "city": city,
                    "country": country,
                    "lat": city_data["lat"],
                    "lon": city_data["lon"],
                    "timezone": city_data["timezone"]
                })
    
    return {"results": results[:20]}  # Limit to 20 results

@app.get("/api/datas")
async def get_all_datas():
    """Get all countries, cities data, and timezones for initial load"""
    return {
        "countries": sorted(list(COUNTRIES_AND_CITIES.keys())),
        "cities_data": COUNTRIES_AND_CITIES,
        "timezones": sorted(TIMEZONES)
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "3.0.0"}
