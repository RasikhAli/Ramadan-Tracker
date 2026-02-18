from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import pytz
import httpx
import json
from typing import Optional, Dict, Any, List
from app.data.cities import COUNTRIES_AND_CITIES, TIMEZONES, FIQH_METHODS, get_timezone_for_coordinates

app = FastAPI(
    title="Ramadan Countdown API",
    description="Dynamic Ramadan countdown for Sehri and Iftar times with auto-detection",
    version="2.0.0"
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

def get_cache_key(lat: float, lon: float, date: str, method: str) -> str:
    """Generate cache key for prayer times"""
    return f"{lat},{lon},{date},{method}"

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

async def fetch_prayer_times(lat: float, lon: float, date: str, timezone: str, fiqh_method: str) -> Dict[str, Any]:
    """Fetch prayer times from API - using Aladhan API"""
    cache_key = get_cache_key(lat, lon, date, fiqh_method)
    
    # Check cache
    if cache_key in prayer_time_cache:
        cached_data = prayer_time_cache[cache_key]
        if cached_data.get("date") == date:
            return cached_data
    
    # Determine calculation method based on fiqh
    # school: 0 = Shafi (standard), 1 = Hanafi
    # method: Different calculation methods
    
    # Method parameters:
    # 0 = Shafi (University of Islamic Sciences, Karachi)
    # 1 = Muslim World League
    # 2 = Islamic Society of North America (ISNA)
    # 3 = Egyptian General Authority
    # 4 = Umm Al-Qura University, Makkah
    # 5 = University of Islamic Sciences, Karachi
    # 7 = Tehran (Institute of Geophysics, University of Tehran) - Shia/Iran method
    # 8 = Shia (Shia Ithna Ashari, Leva Research Institute)
    # 9 = Shia (Institute of Geophysics, University of Tehran)
    
    method_map = {
        "hanafi": {"method": 2, "school": 1},  # ISNA with Hanafi school
        "jaffari": {"method": 8, "school": 1},  # Shia Ithna Ashari method (Leva Research Institute)
        "shafi": {"method": 2, "school": 0}  # ISNA with Shafi school
    }
    
    fiqh_config = method_map.get(fiqh_method, method_map["shafi"])
    
    url = "https://api.aladhan.com/v1/timings"
    params = {
        "latitude": lat,
        "longitude": lon,
        "method": fiqh_config["method"],
        "school": fiqh_config["school"],
        "date": date,
        "timezone": timezone
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("code") == 200:
                    timings = data.get("data", {}).get("timings", {})
                    date_info = data.get("data", {}).get("date", {})
                    
                    # For Jaffari, add 10 minutes to Maghrib as per traditional Shia practice
                    maghrib_time = timings.get("Maghrib", "")
                    if fiqh_method == "jaffari" and maghrib_time:
                        try:
                            from datetime import timedelta
                            maghrib_dt = datetime.strptime(maghrib_time, "%H:%M")
                            maghrib_dt += timedelta(minutes=10)
                            maghrib_time = maghrib_dt.strftime("%H:%M")
                        except:
                            pass
                    
                    result = {
                        "date": date,
                        "timings": {
                            "Fajr": timings.get("Fajr", ""),
                            "Sunrise": timings.get("Sunrise", ""),
                            "Dhuhr": timings.get("Dhuhr", ""),
                            "Asr": timings.get("Asr", ""),
                            "Maghrib": timings.get("Maghrib", ""),
                            "Isha": timings.get("Isha", ""),
                        },
                        "timings_12h": {
                            "Fajr": convert_to_12_hour(timings.get("Fajr", "")),
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
                        "iftar": maghrib_time,
                        "iftar_12h": convert_to_12_hour(maghrib_time)
                    }
                    
                    # Cache the result
                    prayer_time_cache[cache_key] = result
                    
                    return result
                else:
                    raise HTTPException(status_code=400, detail="API returned error")
            else:
                raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch prayer times: {response.status_code}")
                
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"API request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

async def detect_location_from_ip() -> Optional[Dict[str, Any]]:
    """Detect user location from IP address"""
    try:
        # Try multiple IP geolocation services
        services = [
            "https://ipapi.co/json/",
            "http://ip-api.com/json/"
        ]
        
        for service_url in services:
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    response = await client.get(service_url)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check if we got valid coordinates
                        lat = data.get("latitude") or data.get("lat", 0)
                        lon = data.get("longitude") or data.get("lon", 0)
                        
                        if lat and lon and lat != 0:
                            # Extract relevant info
                            result = {
                                "ip": data.get("ip", ""),
                                "city": data.get("city", ""),
                                "region": data.get("region", data.get("region_name", "")),
                                "country": data.get("country_name", data.get("country", "")),
                                "country_code": data.get("country_code", ""),
                                "latitude": lat,
                                "longitude": lon,
                                "timezone": data.get("timezone", ""),
                                "is_mobile": data.get("mobile", False)
                            }
                            
                            # Find closest city from our database
                            closest_city = find_closest_city(lat, lon)
                            if closest_city:
                                result["detected_city"] = closest_city["city"]
                                result["detected_country"] = closest_city["country"]
                                result["detected_lat"] = closest_city["lat"]
                                result["detected_lon"] = closest_city["lon"]
                                result["detected_timezone"] = closest_city["timezone"]
                            
                            return result
            except:
                continue
        
        return None
    except Exception as e:
        print(f"Error detecting location: {e}")
        return None

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
    """Auto-detect user location based on IP and browser timezone"""
    # First try IP-based detection
    ip_location = await detect_location_from_ip()
    
    # If IP detection fails, use browser timezone
    if not ip_location or not ip_location.get("detected_city"):
        browser_tz = browser_timezone or "UTC"
        
        # Try to find a city matching the browser timezone
        for country, country_data in COUNTRIES_AND_CITIES.items():
            for city, city_data in country_data["cities"].items():
                if city_data["timezone"] == browser_tz:
                    return {
                        "detected": False,
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
    
    return {
        "detected": True,
        "method": "ip",
        "detected_city": ip_location.get("detected_city", ""),
        "detected_country": ip_location.get("detected_country", ""),
        "detected_lat": ip_location.get("detected_lat", 0),
        "detected_lon": ip_location.get("detected_lon", 0),
        "detected_timezone": ip_location.get("detected_timezone", "UTC"),
        "browser_timezone": browser_timezone,
        "message": f"Location detected: {ip_location.get('detected_city', 'Unknown')}, {ip_location.get('detected_country', 'Unknown')}"
    }

@app.get("/api/countries")
async def get_countries():
    """Get list of available countries"""
    countries = list(COUNTRIES_AND_CITIES.keys())
    return {"countries": countries}

@app.get("/api/cities/{country}")
async def get_cities(country: str):
    """Get cities for a specific country"""
    if country not in COUNTRIES_AND_CITIES:
        raise HTTPException(status_code=404, detail="Country not found")
    
    cities = list(COUNTRIES_AND_CITIES[country]["cities"].keys())
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
    """Get list of available timezones"""
    return {"timezones": TIMEZONES}

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
    format_12h: bool = Query(True)
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
        times = await fetch_prayer_times(lat, lon, date, tz, method)
        # Get iftar from the result (which has Jaffari adjustment already applied)
        iftar_time = times.get("iftar", times["timings"]["Maghrib"])
        iftar_12h = times.get("iftar_12h", convert_to_12_hour(iftar_time)) if format_12h else iftar_time
        
        results[method] = {
            "fiqh_method": method,
            "timings": times["timings"],
            "timings_12h": times.get("timings_12h", {}),
            "sehri_ends": times["timings"]["Fajr"],
            "sehri_ends_12h": convert_to_12_hour(times["timings"]["Fajr"]) if format_12h else times["timings"]["Fajr"],
            "iftar": iftar_time,
            "iftar_12h": iftar_12h
        }
    
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
    format_12h: bool = Query(True)
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
    prayer_times = await fetch_prayer_times(lat, lon, date, tz, fiqh_method)
    
    # Calculate Sehri and Iftar
    fajr = prayer_times["timings"]["Fajr"]
    maghrib = prayer_times["timings"]["Maghrib"]
    
    # For Jaffari, add 10 minutes to Maghrib as per traditional Shia practice
    if fiqh_method == "jaffari":
        maghrib_time = datetime.strptime(maghrib, "%H:%M")
        maghrib_time += timedelta(minutes=10)
        maghrib = maghrib_time.strftime("%H:%M")
    
    # Sehri ends at Fajr time
    sehri_end = fajr
    # Iftar is at Maghrib time  
    iftar = maghrib
    
    # Convert to 12-hour format if requested
    sehri_end_12h = convert_to_12_hour(sehri_end) if format_12h else sehri_end
    iftar_12h = convert_to_12_hour(iftar) if format_12h else iftar
    
    timings_12h = prayer_times.get("timings_12h", {}) if format_12h else prayer_times.get("timings", {})
    
    return {
        "country": country,
        "city": city,
        "date": date,
        "timezone": tz,
        "lat": lat,
        "lon": lon,
        "fiqh_method": fiqh_method,
        "format_12h": format_12h,
        "coordinates": {"lat": lat, "lon": lon},
        "timings": prayer_times["timings"],
        "timings_12h": timings_12h,
        "sehri_ends": sehri_end,
        "sehri_ends_12h": sehri_end_12h,
        "iftar": iftar,
        "iftar_12h": iftar_12h
    }

@app.get("/api/current-time")
async def get_current_time(timezone: Optional[str] = Query(None)):
    """Get current time in specified timezone"""
    if timezone is None:
        return {"current_time": datetime.now().isoformat(), "timezone": "UTC", "formatted_12h": datetime.now().strftime("%I:%M:%M %p")}
    
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        return {
            "current_time": current_time.isoformat(),
            "timezone": timezone,
            "formatted": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "formatted_12h": current_time.strftime("%I:%M:%S %p")
        }
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail="Invalid timezone")

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
    
    return {"results": results, "query": query}

@app.get("/api/timezone-for-coords")
async def get_timezone_for_coords(lat: float = Query(...), lon: float = Query(...)):
    """Get timezone for given coordinates"""
    tz = get_timezone_for_coordinates(lat, lon)
    return {"timezone": tz, "lat": lat, "lon": lon}

@app.get("/api/datas")
async def get_all_data():
    """Get all countries, cities, timezones, and fiqh methods"""
    return {
        "countries": list(COUNTRIES_AND_CITIES.keys()),
        "timezones": TIMEZONES,
        "fiqh_methods": FIQH_METHODS,
        "cities_data": COUNTRIES_AND_CITIES
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
