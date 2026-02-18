"""
Fiqh Service
Handles fiqh-specific calculations including Jaffari derived times.

IMPORTANT: Jaffari times are DERIVED from Hanafi times using fixed offsets:
- Jaffari Sehri = Hanafi Fajr time - 10 minutes
- Jaffari Iftar = Hanafi Maghrib time + 10 minutes

This is a business rule override, NOT fetched from the API.

Calculation Methods (AlAdhan API method IDs):
- MWL (Muslim World League): 3
- Karachi: 1
- Umm al-Qura: 4
- ISNA: 2
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# Jaffari offset constants (in minutes)
JAFFARI_SEHRI_OFFSET_MINUTES = -10  # Jaffari Sehri is 10 minutes BEFORE Hanafi Fajr
JAFFARI_IFTAR_OFFSET_MINUTES = +10  # Jaffari Iftar is 10 minutes AFTER Hanafi Maghrib

# Calculation method IDs for AlAdhan API
CALCULATION_METHODS = {
    'mwl': {
        'id': 3,
        'name': 'Muslim World League',
        'description': 'Muslim World League. Fajr angle: 18°, Isha angle: 17°'
    },
    'karachi': {
        'id': 1,
        'name': 'University of Islamic Sciences, Karachi',
        'description': 'University of Islamic Sciences, Karachi. Fajr angle: 18°, Isha angle: 18°'
    },
    'umm_al_qura': {
        'id': 4,
        'name': 'Umm al-Qura University, Makkah',
        'description': 'Umm al-Qura University. Fajr angle: 18.5°, Isha: 90 min after Maghrib'
    },
    'isna': {
        'id': 2,
        'name': 'Islamic Society of North America (ISNA)',
        'description': 'Islamic Society of North America. Fajr angle: 15°, Isha angle: 15°'
    },
}


class FiqhService:
    """Service for fiqh-specific calculations."""
    
    @staticmethod
    def apply_time_offset(time_str: str, offset_minutes: int) -> str:
        """
        Apply a time offset to a time string.
        
        Args:
            time_str: Time in HH:MM format
            offset_minutes: Offset in minutes (positive or negative)
        
        Returns:
            Adjusted time in HH:MM format
        """
        try:
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            
            # Create a datetime for calculation
            dt = datetime(2000, 1, 1, hours, minutes)  # Arbitrary date
            dt = dt + timedelta(minutes=offset_minutes)
            
            return dt.strftime("%H:%M")
        except Exception as e:
            logger.error(f"Error applying time offset: {e}")
            return time_str
    
    @staticmethod
    def calculate_jaffari_times(hanafi_fajr: str, hanafi_maghrib: str) -> Tuple[str, str]:
        """
        Calculate Jaffari times from Hanafi times using fixed offsets.
        
        Business Rule:
        - Jaffari Sehri = Hanafi Fajr - 10 minutes
        - Jaffari Iftar = Hanafi Maghrib + 10 minutes
        
        Args:
            hanafi_fajr: Hanafi Fajr time in HH:MM format
            hanafi_maghrib: Hanafi Maghrib time in HH:MM format
        
        Returns:
            Tuple of (jaffari_sehri, jaffari_iftar) in HH:MM format
        """
        jaffari_sehri = FiqhService.apply_time_offset(hanafi_fajr, JAFFARI_SEHRI_OFFSET_MINUTES)
        jaffari_iftar = FiqhService.apply_time_offset(hanafi_maghrib, JAFFARI_IFTAR_OFFSET_MINUTES)
        
        logger.info(f"Jaffari derived times: Sehri={jaffari_sehri} (Hanafi Fajr {hanafi_fajr} - 10min), "
                    f"Iftar={jaffari_iftar} (Hanafi Maghrib {hanafi_maghrib} + 10min)")
        
        return jaffari_sehri, jaffari_iftar
    
    @staticmethod
    def get_calculation_methods() -> Dict[str, Dict[str, Any]]:
        """Get all available calculation methods."""
        return CALCULATION_METHODS
    
    @staticmethod
    def get_calculation_method_id(method_key: str) -> int:
        """Get AlAdhan API method ID for a calculation method key."""
        method = CALCULATION_METHODS.get(method_key, CALCULATION_METHODS['karachi'])
        return method['id']
    
    @staticmethod
    def get_fiqh_method_config(fiqh_method: str, calculation_method: str = 'karachi') -> Dict[str, Any]:
        """
        Get AlAdhan API configuration for a fiqh method.
        
        Note: Jaffari is NOT fetched from API - it's derived from Hanafi.
        
        Args:
            fiqh_method: One of 'hanafi', 'shafi', 'jaffari'
            calculation_method: One of 'mwl', 'karachi', 'umm_al_qura', 'isna'
        
        Returns:
            Dictionary with 'method' and 'school' for AlAdhan API
        """
        calc_method_id = FiqhService.get_calculation_method_id(calculation_method)
        
        configs = {
            'hanafi': {
                'method': calc_method_id,
                'school': 1,  # Hanafi
                'calculation_method': calculation_method,
                'description': f'Hanafi - {CALCULATION_METHODS[calculation_method]["name"]} with Hanafi Asr',
            },
            'shafi': {
                'method': calc_method_id,
                'school': 0,  # Shafi/Maliki/Hanbali
                'calculation_method': calculation_method,
                'description': f'Shafi/Maliki/Hanbali - {CALCULATION_METHODS[calculation_method]["name"]} with Shafi Asr',
            },
            'jaffari': {
                # Jaffari uses Hanafi API times, then applies offsets
                'method': calc_method_id,
                'school': 1,  # Hanafi (base for derivation)
                'calculation_method': calculation_method,
                'description': f'Jaffari (Shia) - Derived from Hanafi with -10min Sehri, +10min Iftar',
                'is_derived': True,
                'sehri_offset': JAFFARI_SEHRI_OFFSET_MINUTES,
                'iftar_offset': JAFFARI_IFTAR_OFFSET_MINUTES,
            },
        }
        
        return configs.get(fiqh_method, configs['shafi'])
    
    @staticmethod
    def get_disclaimer() -> str:
        """Get the Jaffari disclaimer text."""
        return "Jaffari times in this app are derived by fixed offset from Hanafi (−10 min Sehri, +10 min Iftar)."


# Singleton instance
fiqh_service = FiqhService()
