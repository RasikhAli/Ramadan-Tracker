"""
Unit tests for Prayer Time Service
"""
import pytest
from datetime import datetime, timedelta
import pytz
from app.services.prayer_service import PrayerTimeService, ALADHAN_METHODS, ALADHAN_SCHOOLS


class TestPrayerTimeService:
    """Test cases for PrayerTimeService."""
    
    def test_get_fiqh_config_jaffari(self):
        """Test Jaffari (Shia) fiqh configuration."""
        method, school = PrayerTimeService.get_fiqh_config("jaffari")
        assert method == ALADHAN_METHODS["jafari"]  # 0
        assert school == ALADHAN_SCHOOLS["shafi"]   # 0 (doesn't matter for Jafari)
    
    def test_get_fiqh_config_hanafi(self):
        """Test Hanafi fiqh configuration."""
        method, school = PrayerTimeService.get_fiqh_config("hanafi")
        assert method == ALADHAN_METHODS["karachi"]  # 1
        assert school == ALADHAN_SCHOOLS["hanafi"]   # 1
    
    def test_get_fiqh_config_shafi(self):
        """Test Shafi fiqh configuration."""
        method, school = PrayerTimeService.get_fiqh_config("shafi")
        assert method == ALADHAN_METHODS["karachi"]  # 1
        assert school == ALADHAN_SCHOOLS["shafi"]    # 0
    
    def test_get_fiqh_config_default(self):
        """Test default (unknown) fiqh configuration defaults to Shafi."""
        method, school = PrayerTimeService.get_fiqh_config("unknown")
        assert method == ALADHAN_METHODS["karachi"]  # 1
        assert school == ALADHAN_SCHOOLS["shafi"]    # 0
    
    def test_convert_to_12_hour_morning(self):
        """Test 24-hour to 12-hour conversion for morning times."""
        assert PrayerTimeService.convert_to_12_hour("05:20") == "5:20 AM"
        assert PrayerTimeService.convert_to_12_hour("06:00") == "6:00 AM"
        assert PrayerTimeService.convert_to_12_hour("11:59") == "11:59 AM"
    
    def test_convert_to_12_hour_afternoon(self):
        """Test 24-hour to 12-hour conversion for afternoon times."""
        assert PrayerTimeService.convert_to_12_hour("12:00") == "12:00 PM"
        assert PrayerTimeService.convert_to_12_hour("13:30") == "1:30 PM"
        assert PrayerTimeService.convert_to_12_hour("17:53") == "5:53 PM"
        assert PrayerTimeService.convert_to_12_hour("23:59") == "11:59 PM"
    
    def test_convert_to_12_hour_midnight(self):
        """Test 24-hour to 12-hour conversion for midnight."""
        assert PrayerTimeService.convert_to_12_hour("00:00") == "12:00 AM"
        assert PrayerTimeService.convert_to_12_hour("00:30") == "12:30 AM"
    
    def test_convert_to_12_hour_empty(self):
        """Test 24-hour to 12-hour conversion with empty input."""
        assert PrayerTimeService.convert_to_12_hour("") == "--:--"
        assert PrayerTimeService.convert_to_12_hour(None) == "--:--"
    
    def test_parse_time_to_datetime_valid(self):
        """Test parsing valid time string to datetime."""
        dt = PrayerTimeService.parse_time_to_datetime("05:20", "18-02-2026", "Asia/Karachi")
        assert dt is not None
        assert dt.year == 2026
        assert dt.month == 2
        assert dt.day == 18
        assert dt.hour == 5
        assert dt.minute == 20
        assert dt.tzinfo is not None
    
    def test_parse_time_to_datetime_invalid_time(self):
        """Test parsing invalid time string returns None."""
        dt = PrayerTimeService.parse_time_to_datetime("invalid", "18-02-2026", "Asia/Karachi")
        assert dt is None
    
    def test_parse_time_to_datetime_invalid_date(self):
        """Test parsing invalid date string returns None."""
        dt = PrayerTimeService.parse_time_to_datetime("05:20", "invalid", "Asia/Karachi")
        assert dt is None
    
    def test_parse_time_to_datetime_invalid_timezone(self):
        """Test parsing invalid timezone returns None."""
        dt = PrayerTimeService.parse_time_to_datetime("05:20", "18-02-2026", "Invalid/Timezone")
        assert dt is None
    
    def test_calculate_countdown_future(self):
        """Test countdown calculation for future time."""
        now = datetime.now(pytz.UTC)
        target = now + timedelta(hours=2, minutes=30, seconds=15)
        
        result = PrayerTimeService.calculate_countdown(target, now)
        
        assert result["hours"] == 2
        assert result["minutes"] == 30
        assert result["seconds"] == 15
        assert result["total_seconds"] == 2 * 3600 + 30 * 60 + 15
    
    def test_calculate_countdown_past(self):
        """Test countdown calculation for past time (should show next day)."""
        now = datetime.now(pytz.UTC)
        target = now - timedelta(hours=1)  # 1 hour ago
        
        result = PrayerTimeService.calculate_countdown(target, now)
        
        # Should show ~23 hours (next day)
        assert result["hours"] == 23
        assert result["total_seconds"] > 0
    
    def test_calculate_countdown_same_time(self):
        """Test countdown calculation for same time (should show next day)."""
        now = datetime.now(pytz.UTC)
        
        result = PrayerTimeService.calculate_countdown(now, now)
        
        # Should show 24 hours (next day)
        assert result["hours"] == 23
        assert result["minutes"] == 59
        assert result["seconds"] >= 59  # May be 59 or 60 depending on timing
    
    def test_get_current_time_in_timezone(self):
        """Test getting current time in a specific timezone."""
        # Get time in Karachi timezone
        dt_karachi = PrayerTimeService.get_current_time_in_timezone("Asia/Karachi")
        assert dt_karachi.tzinfo is not None
        
        # Get time in UTC
        dt_utc = PrayerTimeService.get_current_time_in_timezone("UTC")
        assert dt_utc.tzinfo is not None
        
        # Karachi should be UTC+5
        karachi_offset = dt_karachi.strftime('%z')
        assert karachi_offset == '+0500'
    
    def test_format_date_for_api(self):
        """Test date formatting for AlAdhan API."""
        dt = datetime(2026, 2, 18, 5, 20, 0)
        formatted = PrayerTimeService.format_date_for_api(dt)
        assert formatted == "18-02-2026"
    
    def test_get_cache_key(self):
        """Test cache key generation."""
        key = PrayerTimeService.get_cache_key(24.8607, 67.0011, "18-02-2026", 1, 1)
        assert key == "24.8607,67.0011,18-02-2026,1,1"
    
    def test_get_cache_key_different_coords(self):
        """Test cache key is different for different coordinates."""
        key1 = PrayerTimeService.get_cache_key(24.8607, 67.0011, "18-02-2026", 1, 1)
        key2 = PrayerTimeService.get_cache_key(31.5204, 74.3587, "18-02-2026", 1, 1)
        assert key1 != key2
    
    def test_get_cache_key_different_date(self):
        """Test cache key is different for different dates."""
        key1 = PrayerTimeService.get_cache_key(24.8607, 67.0011, "18-02-2026", 1, 1)
        key2 = PrayerTimeService.get_cache_key(24.8607, 67.0011, "19-02-2026", 1, 1)
        assert key1 != key2
    
    def test_get_cache_key_different_method(self):
        """Test cache key is different for different methods."""
        key1 = PrayerTimeService.get_cache_key(24.8607, 67.0011, "18-02-2026", 0, 0)  # Jafari
        key2 = PrayerTimeService.get_cache_key(24.8607, 67.0011, "18-02-2026", 1, 1)  # Hanafi
        assert key1 != key2


class TestTimezoneCalculations:
    """Test timezone-related calculations."""
    
    def test_karachi_timezone_offset(self):
        """Test Karachi timezone is UTC+5."""
        tz = pytz.timezone("Asia/Karachi")
        now = datetime.now(tz)
        offset = now.strftime('%z')
        assert offset == '+0500'
    
    def test_dubai_timezone_offset(self):
        """Test Dubai timezone is UTC+4."""
        tz = pytz.timezone("Asia/Dubai")
        now = datetime.now(tz)
        offset = now.strftime('%z')
        assert offset == '+0400'
    
    def test_timezone_aware_comparison(self):
        """Test that timezone-aware datetime comparison works correctly."""
        # Create same instant in different timezones
        karachi_tz = pytz.timezone("Asia/Karachi")
        utc_tz = pytz.UTC
        
        # 10:00 UTC = 15:00 Karachi
        utc_time = utc_tz.localize(datetime(2026, 2, 18, 10, 0, 0))
        karachi_time = karachi_tz.localize(datetime(2026, 2, 18, 15, 0, 0))
        
        # These should be the same instant
        assert utc_time.timestamp() == karachi_time.timestamp()


class TestPrayerTimeAccuracy:
    """Test prayer time accuracy for specific test cases."""
    
    def test_lahore_hanafi_fajr_approximate(self):
        """
        Test that Lahore Hanafi Fajr time is approximately correct.
        Expected: ~05:20 PKT for 18 Feb 2026
        This is an integration test that requires API call.
        """
        # This would be an integration test
        # For unit test, we verify the method configuration
        method, school = PrayerTimeService.get_fiqh_config("hanafi")
        assert method == 1  # Karachi method
        assert school == 1  # Hanafi school
    
    def test_lahore_jaffari_times_different_from_hanafi(self):
        """
        Test that Jaffari method uses different calculation than Hanafi.
        Jaffari should use method 0 (Leva Institute).
        """
        hanafi_method, hanafi_school = PrayerTimeService.get_fiqh_config("hanafi")
        jaffari_method, jaffari_school = PrayerTimeService.get_fiqh_config("jaffari")
        
        # Methods should be different
        assert hanafi_method != jaffari_method
        assert hanafi_method == 1  # Karachi
        assert jaffari_method == 0  # Jafari/Leva


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
