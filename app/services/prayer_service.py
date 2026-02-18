"""
Prayer Time Service Layer
Handles all prayer time calculations and API interactions.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import pytz
import httpx
import logging

logger = logging.getLogger(__name__)

# AlAdhan API Method IDs
ALADHAN_METHODS = {
    "jafari": 0,        # Shia Ithna-Ashari, Leva Institute, Qum
    "karachi": 1,       # University of Islamic Sciences, Karachi
    "isna": 2,          # Islamic Society of North America
    "mwl": 3,           # Muslim World League
    "makkah": 4,        # Umm Al-Qura University, Makkah
    "egypt": 5,         # Egyptian General Authority of Survey
    "tehran": 7,        # Institute of Geophysics, University of Tehran
    "gulf": 8,          # Gulf Region
    "kuwait": 9,        # Kuwait
    "qatar": 10,        # Qatar
    "singapore": 11,    # Majlis Ugama Islam Singapura
    "france": 12,       # Union Organization islamic de France
    "turkey": 13,       # Diyanet İşleri Başkanlığı
    "russia": 14,       # Spiritual Administration of Muslims of Russia
}

# AlAdhan School IDs (for Asr calculation)
ALADHAN_SCHOOLS = {
    "shafi": 0,         # Shafi, Maliki, Hanbali (standard)
    "hanafi": 1,        # Hanafi
}


class PrayerTimeService:
    """Service for fetching and calculating prayer times."""
    
    CACHE: Dict[str, Any] = {}
    CACHE_ENABLED = True
    
    @staticmethod
    def get_fiqh_config(fiqh_method: str) -> Tuple[int, int]:
        """
        Get AlAdhan method and school parameters for a given fiqh method.
        
        Args:
            fiqh_method: One of 'hanafi', 'shafi', 'jaffari'
        
        Returns:
            Tuple of (method_id, school_id)
        """
        if fiqh_method == "jaffari":
            # Jafari (Shia) - uses Leva Institute calculations
            return (ALADHAN_METHODS["jafari"], ALADHAN_SCHOOLS["shafi"])
        elif fiqh_method == "hanafi":
            # Hanafi - uses Karachi method with Hanafi Asr
            return (ALADHAN_METHODS["karachi"], ALADHAN_SCHOOLS["hanafi"])
        else:
            # Shafi/Maliki/Hanbali - uses Karachi method with Shafi Asr
            return (ALADHAN_METHODS["karachi"], ALADHAN_SCHOOLS["shafi"])
    
    @staticmethod
    def get_cache_key(lat: float, lon: float, date: str, method: int, school: int) -> str:
        """Generate a cache key for prayer times."""
        return f"{lat:.4f},{lon:.4f},{date},{method},{school}"
    
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
    def parse_time_to_datetime(time_str: str, date_str: str, timezone_str: str) -> Optional[datetime]:
        """
        Parse a time string (HH:MM) into a timezone-aware datetime object.
        
        Args:
            time_str: Time in HH:MM format
            date_str: Date in DD-MM-YYYY format
            timezone_str: Timezone string (e.g., "Asia/Karachi")
        
        Returns:
            Timezone-aware datetime object or None if parsing fails
        """
        try:
            tz = pytz.timezone(timezone_str)
            day, month, year = map(int, date_str.split('-'))
            hours, minutes = map(int, time_str.split(':'))
            
            dt = datetime(year, month, day, hours, minutes, 0)
            return tz.localize(dt)
        except Exception as e:
            logger.error(f"Error parsing time '{time_str}' with date '{date_str}': {e}")
            return None
    
    @staticmethod
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
        # Make sure both times are timezone-aware
        if target_time.tzinfo is None or current_time.tzinfo is None:
            logger.warning("Countdown called with naive datetime objects")
        
        if target_time <= current_time:
            # Target has passed, calculate for next day
            target_time = target_time + timedelta(days=1)
        
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
    
    @staticmethod
    def get_current_time_in_timezone(timezone_str: str) -> datetime:
        """
        Get current time in the specified timezone.
        
        Args:
            timezone_str: Timezone string (e.g., "Asia/Karachi")
        
        Returns:
            Timezone-aware datetime object
        """
        tz = pytz.timezone(timezone_str)
        return datetime.now(tz)
    
    @staticmethod
    def format_date_for_api(dt: datetime) -> str:
        """Format datetime to DD-MM-YYYY format for AlAdhan API."""
        return dt.strftime("%d-%m-%Y")
    
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
            method: Calculation method ID
            school: School ID (0=Shafi, 1=Hanafi)
            timeout: Request timeout in seconds
        
        Returns:
            Raw API response data
        
        Raises:
            HTTPException: If API request fails
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
                
                logger.info(f"AlAdhan API Response: {data.get('data', {}).get('timings', {})}")
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
        include_debug: bool = False
    ) -> Dict[str, Any]:
        """
        Get prayer times for a specific location and fiqh method.
        
        Args:
            lat: Latitude
            lon: Longitude
            date: Date in DD-MM-YYYY format
            timezone: Timezone string
            fiqh_method: One of 'hanafi', 'shafi', 'jaffari'
            include_debug: Whether to include debug information
        
        Returns:
            Processed prayer times data
        """
        method, school = self.get_fiqh_config(fiqh_method)
        
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
        
        # Sehri ends at Fajr - use directly from API
        fajr_time = timings.get("Fajr", "")
        # Iftar is at Maghrib - use directly from API
        maghrib_time = timings.get("Maghrib", "")
        
        # Parse times to datetime for countdown
        fajr_dt = self.parse_time_to_datetime(fajr_time, date, timezone)
        maghrib_dt = self.parse_time_to_datetime(maghrib_time, date, timezone)
        
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
            "sehri_ends": fajr_time,
            "sehri_ends_12h": self.convert_to_12_hour(fajr_time),
            "iftar": maghrib_time,
            "iftar_12h": self.convert_to_12_hour(maghrib_time),
            "fajr_datetime": fajr_dt.isoformat() if fajr_dt else None,
            "maghrib_datetime": maghrib_dt.isoformat() if maghrib_dt else None,
        }
        
        if include_debug:
            result["debug"] = {
                "raw_timings": timings,
                "meta": meta,
                "fajr_parsed": fajr_dt.isoformat() if fajr_dt else None,
                "maghrib_parsed": maghrib_dt.isoformat() if maghrib_dt else None,
            }
        
        return result


# Singleton instance
prayer_service = PrayerTimeService()
