"""
Prayer Time Service
Handles prayer time fetching from AlAdhan API.

IMPORTANT: 
- Hanafi and Shafi times are fetched from AlAdhan API
- Jaffari times are DERIVED from Hanafi times (handled by FiqhService)
- Sehri ends EXACTLY at Fajr time (no arbitrary subtraction)
- Iftar is EXACTLY at Maghrib time (no manual offsets)
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pytz
import httpx
import logging

from app.services.fiqh_service import FiqhService, JAFFARI_SEHRI_OFFSET_MINUTES, JAFFARI_IFTAR_OFFSET_MINUTES

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class PrayerTimeService:
    """Service for fetching prayer times from AlAdhan API."""
    
    CACHE: Dict[str, Any] = {}
    CACHE_ENABLED = True
    
    @staticmethod
    def convert_to_12_hour(time_24: str) -> str:
        """Convert 24-hour time to 12-hour format."""
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
        except Exception:
            return time_24
    
    @staticmethod
    def get_cache_key(lat: float, lon: float, date: str, method: int, school: int) -> str:
        """Generate a cache key for prayer times."""
        return f"{lat:.4f},{lon:.4f},{date},{method},{school}"
    
    async def fetch_from_aladhan(
        self,
        lat: float,
        lon: float,
        date: str,
        timezone: str,
        method: int,
        school: int,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Fetch prayer times from AlAdhan API.
        
        Args:
            lat: Latitude
            lon: Longitude
            date: Date in DD-MM-YYYY format
            timezone: Timezone string
            method: Calculation method ID (1 = Karachi)
            school: School ID (0 = Shafi, 1 = Hanafi)
            timeout: Request timeout in seconds
        
        Returns:
            Raw API response data
        """
        cache_key = self.get_cache_key(lat, lon, date, method, school)
        
        # Check cache
        if self.CACHE_ENABLED and cache_key in self.CACHE:
            cached = self.CACHE[cache_key]
            if cached.get("date") == date:
                logger.info(f"Cache hit for {cache_key}")
                return cached
        
        url = "https://api.aladhan.com/v1/timings"
        params = {
            "latitude": lat,
            "longitude": lon,
            "method": method,
            "school": school,
            "date": date,
            "timezone": timezone
        }
        
        logger.info(f"AlAdhan API Request: {url}")
        logger.info(f"Params: lat={lat}, lon={lon}, method={method}, school={school}, date={date}, tz={timezone}")
        
        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.get(url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"AlAdhan API HTTP Error: {response.status_code}")
                    raise Exception(f"API returned status {response.status_code}")
                
                data = response.json()
                
                if data.get("code") != 200:
                    error = data.get("data", "Unknown error")
                    logger.error(f"AlAdhan API Error: {error}")
                    raise Exception(f"API error: {error}")
                
                # Cache the result
                if self.CACHE_ENABLED:
                    self.CACHE[cache_key] = data
                
                logger.info(f"AlAdhan API Response timings: {data.get('data', {}).get('timings', {})}")
                return data
                
        except httpx.RequestError as e:
            logger.error(f"AlAdhan Request Error: {e}")
            raise Exception(f"Request failed: {e}")
    
    async def get_prayer_times(
        self,
        lat: float,
        lon: float,
        date: str,
        timezone: str,
        fiqh_method: str,
        calculation_method: str = 'mwl',
        include_debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get prayer times for a specific location and fiqh method.
        
        For Jaffari: Times are derived from Hanafi using fixed offsets.
        
        Args:
            lat: Latitude
            lon: Longitude
            date: Date in DD-MM-YYYY format
            timezone: Timezone string
            fiqh_method: One of 'hanafi', 'shafi', 'jaffari'
            calculation_method: One of 'mwl', 'karachi', 'umm_al_qura', 'isna'
            include_debug: Whether to include debug information
        
        Returns:
            Processed prayer times data
        """
        # Get fiqh configuration
        fiqh_config = FiqhService.get_fiqh_method_config(fiqh_method, calculation_method)
        method = fiqh_config['method']
        school = fiqh_config['school']
        
        # Fetch from API
        raw_data = await self.fetch_from_aladhan(
            lat=lat,
            lon=lon,
            date=date,
            timezone=timezone,
            method=method,
            school=school
        )
        
        timings = raw_data.get("data", {}).get("timings", {})
        meta = raw_data.get("data", {}).get("meta", {})
        date_info = raw_data.get("data", {}).get("date", {})
        
        # Extract Hijri date information
        hijri = date_info.get("hijri", {})
        gregorian = date_info.get("gregorian", {})
        
        # Get Fajr and Maghrib times
        fajr_time = timings.get("Fajr", "")
        maghrib_time = timings.get("Maghrib", "")
        
        # For Jaffari, apply offsets to derive times
        if fiqh_method == "jaffari":
            jaffari_sehri, jaffari_iftar = FiqhService.calculate_jaffari_times(fajr_time, maghrib_time)
            sehri_time = jaffari_sehri
            iftar_time = jaffari_iftar
            logger.info(f"Jaffari derived: Sehri={sehri_time}, Iftar={iftar_time}")
        else:
            # For Hanafi and Shafi, Sehri = Fajr, Iftar = Maghrib
            sehri_time = fajr_time
            iftar_time = maghrib_time
        
        result = {
            "date": date,
            "timezone": timezone,
            "lat": lat,
            "lon": lon,
            "fiqh_method": fiqh_method,
            "method": method,
            "school": school,
            "timings": {
                "Fajr": fajr_time,
                "Sunrise": timings.get("Sunrise", ""),
                "Dhuhr": timings.get("Dhuhr", ""),
                "Asr": timings.get("Asr", ""),
                "Maghrib": maghrib_time,
                "Isha": timings.get("Isha", ""),
            },
            "timings_12h": {
                "Fajr": self.convert_to_12_hour(fajr_time),
                "Sunrise": self.convert_to_12_hour(timings.get("Sunrise", "")),
                "Dhuhr": self.convert_to_12_hour(timings.get("Dhuhr", "")),
                "Asr": self.convert_to_12_hour(timings.get("Asr", "")),
                "Maghrib": self.convert_to_12_hour(maghrib_time),
                "Isha": self.convert_to_12_hour(timings.get("Isha", "")),
            },
            "sehri_ends": sehri_time,
            "sehri_ends_12h": self.convert_to_12_hour(sehri_time),
            "iftar": iftar_time,
            "iftar_12h": self.convert_to_12_hour(iftar_time),
            "is_derived": fiqh_method == "jaffari",
            # Hijri date from API
            "hijri_date": {
                "date": hijri.get("date", ""),
                "day": hijri.get("day", ""),
                "month": hijri.get("month", {}).get("en", ""),
                "month_number": hijri.get("month", {}).get("number", ""),
                "year": hijri.get("year", ""),
                "format": f"{hijri.get('day', '')} {hijri.get('month', {}).get('en', '')} {hijri.get('year', '')}",
            },
            "gregorian_date": {
                "date": gregorian.get("date", ""),
                "day": gregorian.get("day", ""),
                "month": gregorian.get("month", {}).get("en", ""),
                "year": gregorian.get("year", ""),
                "format": f"{gregorian.get('day', '')} {gregorian.get('month', {}).get('en', '')} {gregorian.get('year', '')}",
            },
        }
        
        if include_debug:
            result["debug"] = {
                "raw_timings": timings,
                "meta": meta,
                "fiqh_config": fiqh_config,
            }
        
        return result


# Singleton instance
prayer_service = PrayerTimeService()
