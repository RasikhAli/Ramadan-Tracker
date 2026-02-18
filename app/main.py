"""
Ramadan Countdown FastAPI Application
Version 4.0.0 - Refactored with Service Layer Architecture

Key Features:
- Browser geolocation for user location detection (not server location)
- Offline city data from GeoNames (cities with population > 15000)
- Jaffari times derived from Hanafi using fixed offsets
- Proper timezone handling for all countdown calculations

Jaffari Derivation Rule:
- Jaffari Sehri = Hanafi Fajr - 10 minutes
- Jaffari Iftar = Hanafi Maghrib + 10 minutes
- These are fixed offsets, NOT fetched from API
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import pytz
import logging
from typing import Optional, Dict, Any, List

from app.services import (
    city_service,
    prayer_service,
    fiqh_service,
    countdown_service,
    JAFFARI_SEHRI_OFFSET_MINUTES,
    JAFFARI_IFTAR_OFFSET_MINUTES,
)

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# App metadata
APP_VERSION = "4.0.0"

app = FastAPI(
    title="Ramadan Countdown API",
    description="Dynamic Ramadan countdown for Sehri and Iftar times with auto-detection",
    version=APP_VERSION
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

# Fiqh methods available
FIQH_METHODS = ["hanafi", "shafi", "jaffari"]


# ============================================================================
# Routes
# ============================================================================

@app.get("/")
async def root():
    """Render the main page"""
    from fastapi.requests import Request
    return templates.TemplateResponse("index.html", {"request": {}})


# ============================================================================
# Location Detection APIs
# ============================================================================

@app.get("/api/detect-location")
async def detect_location(browser_timezone: Optional[str] = Query(None)):
    """
    Auto-detect user location based on browser timezone.
    This is a fallback when geolocation is not available.
    """
    browser_tz = browser_timezone or "UTC"
    
    # Try to find a city matching the browser timezone
    city_match = city_service.find_city_by_timezone(browser_tz)
    
    if city_match:
        return {
            "detected": True,
            "method": "timezone",
            "detected_city": city_match["city"],
            "detected_country": city_match["country"],
            "detected_lat": city_match["lat"],
            "detected_lon": city_match["lon"],
            "detected_timezone": city_match["timezone"],
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
    """
    Detect user location from browser-provided coordinates.
    Uses the Geolocation API on the client side.
    """
    # Find closest city from our database
    closest_city = city_service.find_closest_city(lat, lon)
    
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
    city_match = city_service.find_city_by_timezone(browser_tz)
    
    if city_match:
        return {
            "detected": True,
            "method": "timezone_fallback",
            "detected_city": city_match["city"],
            "detected_country": city_match["country"],
            "detected_lat": city_match["lat"],
            "detected_lon": city_match["lon"],
            "detected_timezone": city_match["timezone"],
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


# ============================================================================
# City Data APIs
# ============================================================================

@app.get("/api/countries")
async def get_countries():
    """Get list of available countries sorted alphabetically"""
    countries = city_service.get_countries()
    return {"countries": countries}


@app.get("/api/cities/{country}")
async def get_cities(country: str):
    """Get cities for a specific country sorted alphabetically"""
    cities = city_service.get_city_names_for_country(country)
    
    if not cities:
        raise HTTPException(status_code=404, detail="Country not found")
    
    return {"cities": cities, "country": country}


@app.get("/api/city-data")
async def get_city_data(country: str = Query(...), city: str = Query(...)):
    """Get city coordinates and timezone"""
    city_data = city_service.get_city_data(country, city)
    
    if not city_data:
        raise HTTPException(status_code=404, detail="City or country not found")
    
    return city_data


@app.get("/api/search-city")
async def search_city(query: str = Query(...)):
    """Search for a city by name"""
    results = city_service.search_cities(query, limit=20)
    return {"results": results}


@app.get("/api/datas")
async def get_all_datas():
    """Get all countries, cities data for initial load"""
    data = city_service.get_all_data()
    return {
        "countries": data["countries"],
        "cities_data": data["cities_data"]
    }


# ============================================================================
# Fiqh Methods API
# ============================================================================

@app.get("/api/fiqh-methods")
async def get_fiqh_methods():
    """Get list of fiqh methods with descriptions"""
    from app.services.fiqh_service import FiqhService, CALCULATION_METHODS
    return {
        "methods": FIQH_METHODS,
        "descriptions": {
            "hanafi": "Hanafi school with selected calculation method",
            "shafi": "Shafi/Maliki/Hanbali school with selected calculation method",
            "jaffari": "Jaffari (Shia) - Derived from Hanafi with fixed offsets"
        },
        "calculation_methods": CALCULATION_METHODS,
        "jaffari_derivation": {
            "note": "Jaffari times are derived from Hanafi times using fixed offsets",
            "sehri_offset_minutes": JAFFARI_SEHRI_OFFSET_MINUTES,
            "iftar_offset_minutes": JAFFARI_IFTAR_OFFSET_MINUTES,
            "formula": {
                "jaffari_sehri": "Hanafi Fajr - 10 minutes",
                "jaffari_iftar": "Hanafi Maghrib + 10 minutes"
            }
        }
    }


# ============================================================================
# Prayer Times APIs
# ============================================================================

@app.get("/api/prayer-times")
async def get_prayer_times(
    country: str = Query(...),
    city: str = Query(...),
    fiqh_method: str = Query("hanafi"),
    calculation_method: str = Query("mwl"),
    date: Optional[str] = Query(None),
    timezone: Optional[str] = Query(None),
    format_12h: bool = Query(True),
    debug: bool = Query(False)
):
    """
    Get prayer times for a specific city and date.
    
    For Jaffari method:
    - Times are derived from Hanafi using fixed offsets
    - Sehri = Hanafi Fajr - 10 minutes
    - Iftar = Hanafi Maghrib + 10 minutes
    
    Calculation Methods:
    - mwl: Muslim World League
    - karachi: University of Islamic Sciences, Karachi
    - umm_al_qura: Umm al-Qura University, Makkah
    - isna: Islamic Society of North America
    """
    # Get city data
    city_data = city_service.get_city_data(country, city)
    if not city_data:
        raise HTTPException(status_code=404, detail="City or country not found")
    
    lat = city_data["lat"]
    lon = city_data["lon"]
    default_tz = city_data["timezone"]
    
    # Use provided timezone or default
    tz = timezone if timezone else default_tz
    
    # Get date (default to today in city timezone)
    if date is None:
        now = countdown_service.get_current_time_in_timezone(tz)
        date = now.strftime("%d-%m-%Y")
    else:
        # Validate date format
        try:
            datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use DD-MM-YYYY")
    
    # Validate fiqh method
    if fiqh_method not in FIQH_METHODS:
        raise HTTPException(status_code=400, detail=f"Invalid fiqh method. Use one of: {FIQH_METHODS}")
    
    # Fetch prayer times
    try:
        prayer_times = await prayer_service.get_prayer_times(
            lat=lat,
            lon=lon,
            date=date,
            timezone=tz,
            fiqh_method=fiqh_method,
            calculation_method=calculation_method,
            include_debug=debug
        )
    except Exception as e:
        logger.error(f"Failed to fetch prayer times: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch prayer times: {str(e)}")
    
    # Adjust Hijri date based on Maghrib (Islamic day changes at Maghrib, not midnight)
    maghrib_time = prayer_times["timings"]["Maghrib"]
    islamic_day_offset = countdown_service.get_islamic_date_offset(maghrib_time, date, tz)
    
    # Adjust the Hijri date based on offset (-1 = before Maghrib, 0 = after Maghrib)
    hijri_date = prayer_times.get("hijri_date", {})
    if islamic_day_offset != 0 and hijri_date:
        hijri_day = int(hijri_date.get("day", 1)) + islamic_day_offset
        hijri_month_num = int(hijri_date.get("month_number", 9))
        hijri_year = int(hijri_date.get("year", 1447))
        
        # Handle month overflow/underflow
        hijri_months = ['Muharram', 'Safar', 'Rabi al-Awwal', 'Rabi al-Thani', 
                        'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', 'Shaban',
                        'Ramadan', 'Shawwal', 'Dhul Qadah', 'Dhul Hijjah']
        
        if hijri_day > 30:
            hijri_day -= 30
            hijri_month_num += 1
            if hijri_month_num > 12:
                hijri_month_num = 1
                hijri_year += 1
        elif hijri_day < 1:
            hijri_month_num -= 1
            if hijri_month_num < 1:
                hijri_month_num = 12
                hijri_year -= 1
            hijri_day += 30
        
        hijri_month_name = hijri_months[hijri_month_num - 1] if 1 <= hijri_month_num <= 12 else hijri_date.get("month", "")
        
        hijri_date = {
            "date": f"{hijri_day}-{hijri_month_num}-{hijri_year}",
            "day": str(hijri_day),
            "month": hijri_month_name,
            "month_number": str(hijri_month_num),
            "year": str(hijri_year),
            "format": f"{hijri_day} {hijri_month_name} {hijri_year}",
        }
    
    result = {
        "country": country,
        "city": city,
        "date": date,
        "timezone": tz,
        "lat": lat,
        "lon": lon,
        "fiqh_method": fiqh_method,
        "calculation_method": calculation_method,
        "method": prayer_times.get("method"),
        "school": prayer_times.get("school"),
        "format_12h": format_12h,
        "coordinates": {"lat": lat, "lon": lon},
        "timings": prayer_times["timings"],
        "timings_12h": prayer_times.get("timings_12h", {}) if format_12h else prayer_times.get("timings", {}),
        "sehri_ends": prayer_times["sehri_ends"],
        "sehri_ends_12h": prayer_times["sehri_ends_12h"] if format_12h else prayer_times["sehri_ends"],
        "iftar": prayer_times["iftar"],
        "iftar_12h": prayer_times["iftar_12h"] if format_12h else prayer_times["iftar"],
        "is_derived": prayer_times.get("is_derived", False),
        "hijri_date": hijri_date,
        "gregorian_date": prayer_times.get("gregorian_date", {}),
        "is_after_maghrib": islamic_day_offset == 0,
    }
    
    if debug:
        result["debug"] = prayer_times.get("debug")
    
    return result


@app.get("/api/prayer-times-all")
async def get_all_fiqh_prayer_times(
    country: str = Query(...),
    city: str = Query(...),
    calculation_method: str = Query("mwl"),
    date: Optional[str] = Query(None),
    timezone: Optional[str] = Query(None),
    format_12h: bool = Query(True),
    debug: bool = Query(False)
):
    """Get prayer times for all fiqh methods"""
    # Get city data
    city_data = city_service.get_city_data(country, city)
    if not city_data:
        raise HTTPException(status_code=404, detail="City or country not found")
    
    lat = city_data["lat"]
    lon = city_data["lon"]
    default_tz = city_data["timezone"]
    
    tz = timezone if timezone else default_tz
    
    # Get date
    if date is None:
        now = countdown_service.get_current_time_in_timezone(tz)
        date = now.strftime("%d-%m-%Y")
    else:
        try:
            datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Fetch times for all three methods
    results = {}
    hijri_date = None
    gregorian_date_info = None
    
    for method in FIQH_METHODS:
        try:
            times = await prayer_service.get_prayer_times(
                lat=lat,
                lon=lon,
                date=date,
                timezone=tz,
                fiqh_method=method,
                calculation_method=calculation_method,
                include_debug=debug
            )
            
            # Get Hijri date from first successful response
            if hijri_date is None and times.get("hijri_date"):
                hijri_date = times["hijri_date"]
                gregorian_date_info = times.get("gregorian_date", {})
            
            results[method] = {
                "fiqh_method": method,
                "method_id": times.get("method"),
                "school_id": times.get("school"),
                "timings": times["timings"],
                "timings_12h": times.get("timings_12h", {}),
                "sehri_ends": times["sehri_ends"],
                "sehri_ends_12h": times["sehri_ends_12h"] if format_12h else times["sehri_ends"],
                "iftar": times["iftar"],
                "iftar_12h": times["iftar_12h"] if format_12h else times["iftar"],
                "is_derived": times.get("is_derived", False),
            }
            
            if debug:
                results[method]["debug"] = times.get("debug")
                
        except Exception as e:
            logger.error(f"Failed to fetch {method} times: {e}")
            results[method] = {"error": str(e)}
    
    # Adjust Hijri date based on Maghrib (Islamic day changes at Maghrib, not midnight)
    # Use Maghrib time from Hanafi method (or first available)
    maghrib_time = None
    for method in FIQH_METHODS:
        if method in results and "timings" in results[method]:
            maghrib_time = results[method]["timings"].get("Maghrib")
            if maghrib_time:
                break
    
    is_after_maghrib = False
    if maghrib_time and hijri_date:
        islamic_day_offset = countdown_service.get_islamic_date_offset(maghrib_time, date, tz)
        is_after_maghrib = islamic_day_offset == 0  # 0 = after Maghrib, -1 = before Maghrib
        
        if islamic_day_offset != 0:  # Before Maghrib, need to adjust
            hijri_day = int(hijri_date.get("day", 1)) + islamic_day_offset
            hijri_month_num = int(hijri_date.get("month_number", 9))
            hijri_year = int(hijri_date.get("year", 1447))
            
            # Handle month overflow/underflow
            hijri_months = ['Muharram', 'Safar', 'Rabi al-Awwal', 'Rabi al-Thani', 
                            'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', 'Shaban',
                            'Ramadan', 'Shawwal', 'Dhul Qadah', 'Dhul Hijjah']
            
            if hijri_day > 30:
                hijri_day -= 30
                hijri_month_num += 1
                if hijri_month_num > 12:
                    hijri_month_num = 1
                    hijri_year += 1
            elif hijri_day < 1:
                hijri_month_num -= 1
                if hijri_month_num < 1:
                    hijri_month_num = 12
                    hijri_year -= 1
                hijri_day += 30
            
            hijri_month_name = hijri_months[hijri_month_num - 1] if 1 <= hijri_month_num <= 12 else hijri_date.get("month", "")
            
            hijri_date = {
                "date": f"{hijri_day}-{hijri_month_num}-{hijri_year}",
                "day": str(hijri_day),
                "month": hijri_month_name,
                "month_number": str(hijri_month_num),
                "year": str(hijri_year),
                "format": f"{hijri_day} {hijri_month_name} {hijri_year}",
            }
    
    return {
        "country": country,
        "city": city,
        "date": date,
        "timezone": tz,
        "lat": lat,
        "lon": lon,
        "calculation_method": calculation_method,
        "format_12h": format_12h,
        "fiqh_times": results,
        "hijri_date": hijri_date or {},
        "gregorian_date": gregorian_date_info or {},
        "is_after_maghrib": is_after_maghrib,
    }


# ============================================================================
# Countdown API
# ============================================================================

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
    
    For Jaffari method:
    - Sehri countdown uses derived time (Hanafi Fajr - 10 min)
    - Iftar countdown uses derived time (Hanafi Maghrib + 10 min)
    """
    # Get city data
    city_data = city_service.get_city_data(country, city)
    if not city_data:
        raise HTTPException(status_code=404, detail="City or country not found")
    
    lat = city_data["lat"]
    lon = city_data["lon"]
    default_tz = city_data["timezone"]
    
    tz = timezone if timezone else default_tz
    
    # Get today's date in city timezone
    now = countdown_service.get_current_time_in_timezone(tz)
    date = now.strftime("%d-%m-%Y")
    
    # Fetch prayer times
    try:
        prayer_times = await prayer_service.get_prayer_times(
            lat=lat,
            lon=lon,
            date=date,
            timezone=tz,
            fiqh_method=fiqh_method
        )
    except Exception as e:
        logger.error(f"Failed to fetch prayer times for countdown: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch prayer times: {str(e)}")
    
    # Get Sehri and Iftar times (already derived for Jaffari)
    sehri_time = prayer_times["sehri_ends"]
    iftar_time = prayer_times["iftar"]
    
    # Parse times to datetime
    sehri_dt = countdown_service.parse_time_to_datetime(sehri_time, date, tz)
    iftar_dt = countdown_service.parse_time_to_datetime(iftar_time, date, tz)
    
    if not sehri_dt or not iftar_dt:
        raise HTTPException(status_code=500, detail="Failed to parse prayer times")
    
    # Determine next event
    current_time = now
    
    # Check if we're before Sehri
    if current_time < sehri_dt:
        next_event = "sehri"
        target_time = sehri_dt
        event_name = "Sehri Ends"
    # Check if we're between Sehri and Iftar
    elif current_time < iftar_dt:
        next_event = "iftar"
        target_time = iftar_dt
        event_name = "Iftar"
    # After Iftar, countdown to next day's Sehri
    else:
        next_event = "sehri"
        # Get tomorrow's date
        tomorrow = now + timedelta(days=1)
        tomorrow_date = tomorrow.strftime("%d-%m-%Y")
        
        # Fetch tomorrow's prayer times
        try:
            tomorrow_prayer = await prayer_service.get_prayer_times(
                lat=lat,
                lon=lon,
                date=tomorrow_date,
                timezone=tz,
                fiqh_method=fiqh_method
            )
            tomorrow_sehri = tomorrow_prayer["sehri_ends"]
            target_time = countdown_service.parse_time_to_datetime(tomorrow_sehri, tomorrow_date, tz)
        except Exception as e:
            logger.warning(f"Failed to fetch tomorrow's times, using approximation: {e}")
            # Fallback: add 24 hours to today's Sehri
            target_time = sehri_dt + timedelta(days=1)
        
        event_name = "Sehri Ends"
    
    # Calculate countdown
    countdown = countdown_service.calculate_countdown(target_time, current_time)
    
    return {
        "next_event": next_event,
        "event_name": event_name,
        "target_time": target_time.isoformat(),
        "target_time_12h": target_time.strftime("%I:%M %p"),
        "current_time": current_time.isoformat(),
        "current_time_12h": current_time.strftime("%I:%M:%S %p"),
        "countdown": countdown,
        "countdown_formatted": countdown_service.format_countdown(countdown),
        "timezone": tz,
        "city": city,
        "country": country,
        "fiqh_method": fiqh_method,
        "is_derived": prayer_times.get("is_derived", False)
    }


# ============================================================================
# Time APIs
# ============================================================================

@app.get("/api/current-time")
async def get_current_time(timezone: Optional[str] = Query(None)):
    """Get current time in specified timezone"""
    if timezone is None:
        return {
            "current_time": datetime.now().isoformat(),
            "timezone": "UTC",
            "formatted_12h": datetime.now().strftime("%I:%M:%S %p")
        }
    
    try:
        current_time = countdown_service.get_current_time_in_timezone(timezone)
        return {
            "current_time": current_time.isoformat(),
            "timezone": timezone,
            "formatted": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "formatted_12h": current_time.strftime("%I:%M:%S %p"),
            "timestamp": current_time.timestamp()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid timezone: {str(e)}")


# ============================================================================
# Health Check
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "services": {
            "city_service": "ok" if city_service.cities_data else "no_data",
            "prayer_service": "ok",
            "fiqh_service": "ok",
            "countdown_service": "ok"
        },
        "jaffari_derivation": {
            "enabled": True,
            "sehri_offset_minutes": JAFFARI_SEHRI_OFFSET_MINUTES,
            "iftar_offset_minutes": JAFFARI_IFTAR_OFFSET_MINUTES
        }
    }


# ============================================================================
# Hijri Date API
# ============================================================================

@app.get("/api/hijri-date")
async def get_hijri_date(
    date: Optional[str] = Query(None),
    timezone: Optional[str] = Query(None),
    maghrib_time: Optional[str] = Query(None, description="Maghrib time in HH:MM format for Islamic date adjustment")
):
    """
    Get Hijri date for a given Gregorian date.
    Uses AlAdhan API for accurate conversion.
    
    IMPORTANT: In Islamic tradition, the day changes at Maghrib (sunset), not midnight.
    If maghrib_time is provided and current time is after Maghrib, the Hijri day is incremented by 1.
    
    Example: 1 Ramadan continues until Maghrib on Feb 19, 2026.
    After Maghrib on Feb 19, it becomes 2 Ramadan.
    """
    # Get current date in timezone if not provided
    tz = timezone or "UTC"
    now = countdown_service.get_current_time_in_timezone(tz)
    if date is None:
        date = now.strftime("%d-%m-%Y")
    
    # Check if we need to adjust for Islamic date (after Maghrib)
    islamic_day_offset = 0
    if maghrib_time:
        islamic_day_offset = countdown_service.get_islamic_date_offset(maghrib_time, date, tz)
    
    # Call AlAdhan API for Hijri date
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Use the gToH endpoint for direct conversion
            day, month, year = date.split('-')
            response = await client.get(
                f"https://api.aladhan.com/v1/gToH",
                params={
                    "date": int(day),
                    "month": int(month),
                    "year": int(year)
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                hijri = data.get("data", {}).get("hijri", {})
                gregorian = data.get("data", {}).get("gregorian", {})
                
                # Apply Islamic day offset if after Maghrib
                hijri_day = int(hijri.get("day", 1)) + islamic_day_offset
                hijri_month_num = int(hijri.get("month", {}).get("number", 9))
                hijri_year = int(hijri.get("year", 1447))
                
                # Handle month overflow
                hijri_months = ['Muharram', 'Safar', 'Rabi al-Awwal', 'Rabi al-Thani', 
                                'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', 'Shaban',
                                'Ramadan', 'Shawwal', 'Dhul Qadah', 'Dhul Hijjah']
                
                if hijri_day > 30:
                    hijri_day -= 30
                    hijri_month_num += 1
                    if hijri_month_num > 12:
                        hijri_month_num = 1
                        hijri_year += 1
                
                hijri_month_name = hijri_months[hijri_month_num - 1] if 1 <= hijri_month_num <= 12 else hijri.get("month", {}).get("en", "")
                
                return {
                    "gregorian_date": date,
                    "hijri_date": f"{hijri_day}-{hijri_month_num}-{hijri_year}",
                    "hijri_day": str(hijri_day),
                    "hijri_month": hijri_month_name,
                    "hijri_month_number": str(hijri_month_num),
                    "hijri_year": str(hijri_year),
                    "hijri_format": f"{hijri_day} {hijri_month_name} {hijri_year}",
                    "gregorian_format": f"{gregorian.get('day', '')} {gregorian.get('month', {}).get('en', '')} {gregorian.get('year', '')}",
                    "weekday_en": hijri.get("weekday", {}).get("en", ""),
                    "islamic_day_offset": islamic_day_offset,
                    "is_after_maghrib": islamic_day_offset == 0,
                }
    except Exception as e:
        logger.error(f"Failed to fetch Hijri date: {e}")
    
    # Fallback: Calculate approximate Hijri date using known reference
    # Reference: 1 Ramadan 1447 = February 18, 2026 (Pakistan moon sighting)
    # IMPORTANT: Islamic day changes at Maghrib, not midnight
    try:
        from datetime import datetime as dt
        day, month, year = map(int, date.split('-'))
        gregorian_date = dt(year, month, day)
        
        # Reference date: February 18, 2026 = 1 Ramadan 1447 (Pakistan)
        ref_date = dt(2026, 2, 18)
        days_diff = (gregorian_date - ref_date).days
        
        # Start from 1 Ramadan 1447
        hijri_year = 1447
        hijri_month = 9  # Ramadan
        hijri_day = 1 + days_diff + islamic_day_offset  # Add offset if after Maghrib
        
        # Handle day overflow/underflow
        hijri_months = ['Muharram', 'Safar', 'Rabi al-Awwal', 'Rabi al-Thani', 
                        'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', 'Shaban',
                        'Ramadan', 'Shawwal', 'Dhul Qadah', 'Dhul Hijjah']
        
        # Simple adjustment for days in month (approx 29-30 days per month)
        while hijri_day > 30:
            hijri_day -= 30
            hijri_month += 1
            if hijri_month > 12:
                hijri_month = 1
                hijri_year += 1
        
        while hijri_day < 1:
            hijri_month -= 1
            if hijri_month < 1:
                hijri_month = 12
                hijri_year -= 1
            hijri_day += 30
        
        hijri_month_name = hijri_months[hijri_month - 1]
        
        return {
            "gregorian_date": date,
            "hijri_date": f"{hijri_day}-{hijri_month}-{hijri_year}",
            "hijri_day": str(hijri_day),
            "hijri_month": hijri_month_name,
            "hijri_month_number": str(hijri_month),
            "hijri_year": str(hijri_year),
            "hijri_format": f"{hijri_day} {hijri_month_name} {hijri_year}",
            "gregorian_format": f"{day} {gregorian_date.strftime('%B')} {year}",
            "weekday_en": gregorian_date.strftime("%A"),
            "islamic_day_offset": islamic_day_offset,
            "is_after_maghrib": islamic_day_offset == 0,
        }
    except Exception as e:
        logger.error(f"Failed to calculate fallback Hijri date: {e}")
        return {"error": "Could not fetch Hijri date", "gregorian_date": date}


# ============================================================================
# Manual Coordinates API
# ============================================================================

@app.get("/api/prayer-times-by-coords")
async def get_prayer_times_by_coords(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    fiqh_method: str = Query("hanafi"),
    calculation_method: str = Query("mwl"),
    date: Optional[str] = Query(None),
    timezone: Optional[str] = Query(None),
    format_12h: bool = Query(True),
    debug: bool = Query(False)
):
    """
    Get prayer times for specific coordinates (manual lat/long input).
    Useful for locations not in the city database.
    """
    # Default timezone to UTC if not provided
    tz = timezone or "UTC"
    
    # Get date (default to today)
    if date is None:
        now = countdown_service.get_current_time_in_timezone(tz)
        date = now.strftime("%d-%m-%Y")
    else:
        try:
            datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use DD-MM-YYYY")
    
    # Validate fiqh method
    if fiqh_method not in FIQH_METHODS:
        raise HTTPException(status_code=400, detail=f"Invalid fiqh method. Use one of: {FIQH_METHODS}")
    
    # Fetch prayer times
    try:
        prayer_times = await prayer_service.get_prayer_times(
            lat=lat,
            lon=lon,
            date=date,
            timezone=tz,
            fiqh_method=fiqh_method,
            calculation_method=calculation_method,
            include_debug=debug
        )
    except Exception as e:
        logger.error(f"Failed to fetch prayer times: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch prayer times: {str(e)}")
    
    # Adjust Hijri date based on Maghrib (Islamic day changes at Maghrib, not midnight)
    maghrib_time = prayer_times["timings"]["Maghrib"]
    islamic_day_offset = countdown_service.get_islamic_date_offset(maghrib_time, date, tz)
    
    # Adjust the Hijri date based on offset (-1 = before Maghrib, 0 = after Maghrib)
    hijri_date = prayer_times.get("hijri_date", {})
    if islamic_day_offset != 0 and hijri_date:
        hijri_day = int(hijri_date.get("day", 1)) + islamic_day_offset
        hijri_month_num = int(hijri_date.get("month_number", 9))
        hijri_year = int(hijri_date.get("year", 1447))
        
        # Handle month overflow/underflow
        hijri_months = ['Muharram', 'Safar', 'Rabi al-Awwal', 'Rabi al-Thani', 
                        'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', 'Shaban',
                        'Ramadan', 'Shawwal', 'Dhul Qadah', 'Dhul Hijjah']
        
        if hijri_day > 30:
            hijri_day -= 30
            hijri_month_num += 1
            if hijri_month_num > 12:
                hijri_month_num = 1
                hijri_year += 1
        elif hijri_day < 1:
            hijri_month_num -= 1
            if hijri_month_num < 1:
                hijri_month_num = 12
                hijri_year -= 1
            hijri_day += 30
        
        hijri_month_name = hijri_months[hijri_month_num - 1] if 1 <= hijri_month_num <= 12 else hijri_date.get("month", "")
        
        hijri_date = {
            "date": f"{hijri_day}-{hijri_month_num}-{hijri_year}",
            "day": str(hijri_day),
            "month": hijri_month_name,
            "month_number": str(hijri_month_num),
            "year": str(hijri_year),
            "format": f"{hijri_day} {hijri_month_name} {hijri_year}",
        }
    
    result = {
        "coordinates": {"lat": lat, "lon": lon},
        "date": date,
        "timezone": tz,
        "fiqh_method": fiqh_method,
        "calculation_method": calculation_method,
        "method": prayer_times.get("method"),
        "school": prayer_times.get("school"),
        "format_12h": format_12h,
        "timings": prayer_times["timings"],
        "timings_12h": prayer_times.get("timings_12h", {}) if format_12h else prayer_times.get("timings", {}),
        "sehri_ends": prayer_times["sehri_ends"],
        "sehri_ends_12h": prayer_times["sehri_ends_12h"] if format_12h else prayer_times["sehri_ends"],
        "iftar": prayer_times["iftar"],
        "iftar_12h": prayer_times["iftar_12h"] if format_12h else prayer_times["iftar"],
        "is_derived": prayer_times.get("is_derived", False),
        "hijri_date": hijri_date,
        "gregorian_date": prayer_times.get("gregorian_date", {}),
        "is_after_maghrib": islamic_day_offset == 0,
    }
    
    if debug:
        result["debug"] = prayer_times.get("debug")
    
    return result
