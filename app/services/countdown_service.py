"""
Countdown Service
Handles all countdown calculations with proper timezone handling.

IMPORTANT: All countdown calculations must:
1. Use server time in UTC
2. Convert to selected city timezone using pytz
3. Compare current time vs prayer time in SAME timezone
4. If prayer time has passed, switch to next day's event
5. Never show negative countdowns

ISLAMIC DATE RULE:
The Islamic day changes at Maghrib (sunset), not midnight.
- Before Maghrib: Current Hijri day
- After Maghrib: Next Hijri day (new Islamic day begins)

Example: 1 Ramadan continues until Maghrib on Feb 19, 2026.
After Maghrib on Feb 19, it becomes 2 Ramadan.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import pytz
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class CountdownService:
    """Service for countdown calculations with timezone awareness."""
    
    @staticmethod
    def get_current_time_in_timezone(timezone_str: str) -> datetime:
        """
        Get current time in the specified timezone.
        
        Args:
            timezone_str: Timezone string (e.g., "Asia/Karachi")
        
        Returns:
            Timezone-aware datetime object
        """
        try:
            tz = pytz.timezone(timezone_str)
            return datetime.now(tz)
        except pytz.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone: {timezone_str}, falling back to UTC")
            return datetime.now(pytz.UTC)
    
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
            Dictionary with hours, minutes, seconds, total_seconds remaining
        """
        # Ensure both times are timezone-aware
        if target_time.tzinfo is None or current_time.tzinfo is None:
            logger.warning("Countdown called with naive datetime objects")
        
        # If target time has passed, calculate for next day
        if target_time <= current_time:
            target_time = target_time + timedelta(days=1)
            logger.debug(f"Target time has passed, using next day: {target_time}")
        
        diff = target_time - current_time
        total_seconds = int(diff.total_seconds())
        
        # Ensure non-negative
        if total_seconds < 0:
            total_seconds = 0
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return {
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': total_seconds,
        }
    
    @staticmethod
    def get_next_event(
        fajr_time: str,
        maghrib_time: str,
        date_str: str,
        timezone_str: str
    ) -> Tuple[str, datetime, datetime]:
        """
        Determine the next event (Sehri or Iftar) and its target time.
        
        Args:
            fajr_time: Fajr time in HH:MM format
            maghrib_time: Maghrib time in HH:MM format
            date_str: Date in DD-MM-YYYY format
            timezone_str: Timezone string
        
        Returns:
            Tuple of (event_name, target_time, current_time)
        """
        current_time = CountdownService.get_current_time_in_timezone(timezone_str)
        
        # Parse prayer times
        fajr_dt = CountdownService.parse_time_to_datetime(fajr_time, date_str, timezone_str)
        maghrib_dt = CountdownService.parse_time_to_datetime(maghrib_time, date_str, timezone_str)
        
        if not fajr_dt or not maghrib_dt:
            logger.error("Failed to parse prayer times")
            return ("unknown", current_time, current_time)
        
        # Determine next event
        if current_time < fajr_dt:
            # Before Fajr - next event is Sehri (Fajr)
            return ("sehri", fajr_dt, current_time)
        elif current_time < maghrib_dt:
            # Between Fajr and Maghrib - next event is Iftar (Maghrib)
            return ("iftar", maghrib_dt, current_time)
        else:
            # After Maghrib - next event is tomorrow's Sehri
            # Calculate tomorrow's date
            tomorrow = current_time + timedelta(days=1)
            tomorrow_date = tomorrow.strftime("%d-%m-%Y")
            
            # Parse tomorrow's Fajr (use same time, different date)
            tomorrow_fajr_dt = CountdownService.parse_time_to_datetime(
                fajr_time, tomorrow_date, timezone_str
            )
            
            if tomorrow_fajr_dt:
                return ("sehri", tomorrow_fajr_dt, current_time)
            else:
                # Fallback: add 24 hours to today's Fajr
                return ("sehri", fajr_dt + timedelta(days=1), current_time)
    
    @staticmethod
    def format_countdown(countdown: Dict[str, int]) -> str:
        """
        Format countdown dictionary to human-readable string.
        
        Args:
            countdown: Dictionary with hours, minutes, seconds
        
        Returns:
            Formatted string like "02:30:45"
        """
        pad = lambda n: str(n).zfill(2)
        return f"{pad(countdown['hours'])}:{pad(countdown['minutes'])}:{pad(countdown['seconds'])}"
    
    @staticmethod
    def format_countdown_with_days(countdown: Dict[str, int]) -> str:
        """
        Format countdown dictionary with days included.
        
        Args:
            countdown: Dictionary with hours, minutes, seconds
        
        Returns:
            Formatted string like "00:02:30:45" (days:hours:minutes:seconds)
        """
        pad = lambda n: str(n).zfill(2)
        days = countdown['total_seconds'] // 86400
        hours = countdown['hours']
        minutes = countdown['minutes']
        seconds = countdown['seconds']
        return f"{pad(days)}:{pad(hours)}:{pad(minutes)}:{pad(seconds)}"
    
    @staticmethod
    def is_after_maghrib(maghrib_time: str, date_str: str, timezone_str: str) -> bool:
        """
        Check if current time is after Maghrib (sunset).
        
        In Islamic tradition, the day changes at Maghrib, not midnight.
        This function determines if we've passed Maghrib for the current date.
        
        Args:
            maghrib_time: Maghrib time in HH:MM format
            date_str: Date in DD-MM-YYYY format
            timezone_str: Timezone string (e.g., "Asia/Karachi")
        
        Returns:
            True if current time is after Maghrib, False otherwise
        """
        current_time = CountdownService.get_current_time_in_timezone(timezone_str)
        maghrib_dt = CountdownService.parse_time_to_datetime(maghrib_time, date_str, timezone_str)
        
        if not maghrib_dt:
            logger.error(f"Failed to parse Maghrib time: {maghrib_time}")
            return False
        
        return current_time >= maghrib_dt
    
    @staticmethod
    def get_islamic_date_offset(maghrib_time: str, date_str: str, timezone_str: str) -> int:
        """
        Get the offset to apply to Hijri day based on Maghrib.
        
        In Islamic tradition, the day changes at Maghrib, not midnight:
        - Before Maghrib: The current time belongs to the PREVIOUS Islamic day
          (night portion before Fajr is part of the previous day)
          offset = -1 (use previous day's Hijri date)
        - After Maghrib: The new Islamic day has begun
          offset = 0 (use current day's Hijri date from API)
        
        Example for Feb 19, 2026 (Pakistan):
        - API returns 2 Ramadan for Feb 19
        - At 00:21 (before Maghrib): Show 1 Ramadan (offset = -1)
        - At 18:30 (after Maghrib): Show 2 Ramadan (offset = 0)
        
        Args:
            maghrib_time: Maghrib time in HH:MM format
            date_str: Date in DD-MM-YYYY format
            timezone_str: Timezone string (e.g., "Asia/Karachi")
        
        Returns:
            -1 if before Maghrib (previous Islamic day), 0 if after Maghrib (current Islamic day)
        """
        return 0 if CountdownService.is_after_maghrib(maghrib_time, date_str, timezone_str) else -1


# Singleton instance
countdown_service = CountdownService()
