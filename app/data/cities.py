# City coordinates and timezone data for Ramadan countdown
# Format: {country: {cities: {city_name: {lat, lon, timezone}}}}

# Timezone mapping for coordinate-based detection
TIMEZONE_COORDS = [
    {"tz": "Pacific/Auckland", "lat_range": (-47.5, -34.0), "lon_range": (166.0, 179.0)},
    {"tz": "Australia/Sydney", "lat_range": (-35.0, -28.0), "lon_range": (145.0, 154.0)},
    {"tz": "Australia/Perth", "lat_range": (-35.0, -30.0), "lon_range": (113.0, 131.0)},
    {"tz": "Asia/Jakarta", "lat_range": (-8.0, 6.0), "lon_range": (95.0, 142.0)},
    {"tz": "Asia/Makassar", "lat_range": (-7.0, 2.0), "lon_range": (118.0, 131.0)},
    {"tz": "Asia/Kuala_Lumpur", "lat_range": (0.5, 7.5), "lon_range": (98.0, 120.0)},
    {"tz": "Asia/Bangkok", "lat_range": (5.0, 21.0), "lon_range": (97.0, 108.0)},
    {"tz": "Asia/Singapore", "lat_range": (1.0, 2.0), "lon_range": (103.0, 105.0)},
    {"tz": "Asia/Kolkata", "lat_range": (6.0, 36.0), "lon_range": (68.0, 98.0)},
    {"tz": "Asia/Karachi", "lat_range": (23.0, 37.0), "lon_range": (60.0, 78.0)},
    {"tz": "Asia/Dhaka", "lat_range": (20.0, 27.0), "lon_range": (87.0, 93.0)},
    {"tz": "Asia/Kathmandu", "lat_range": (26.0, 31.0), "lon_range": (80.0, 89.0)},
    {"tz": "Asia/Colombo", "lat_range": (5.0, 10.0), "lon_range": (79.0, 82.0)},
    {"tz": "Asia/Riyadh", "lat_range": (12.0, 33.0), "lon_range": (34.0, 57.0)},
    {"tz": "Asia/Dubai", "lat_range": (22.0, 27.0), "lon_range": (51.0, 57.0)},
    {"tz": "Asia/Baghdad", "lat_range": (29.0, 38.0), "lon_range": (38.0, 49.0)},
    {"tz": "Asia/Tehran", "lat_range": (25.0, 40.0), "lon_range": (44.0, 64.0)},
    {"tz": "Asia/Kabul", "lat_range": (29.0, 38.0), "lon_range": (60.0, 75.0)},
    {"tz": "Europe/Moscow", "lat_range": (40.0, 75.0), "lon_range": (20.0, 180.0)},
    {"tz": "Europe/Istanbul", "lat_range": (35.0, 43.0), "lon_range": (25.0, 45.0)},
    {"tz": "Europe/Athens", "lat_range": (35.0, 42.0), "lon_range": (19.0, 30.0)},
    {"tz": "Europe/Paris", "lat_range": (42.0, 52.0), "lon_range": (-5.0, 10.0)},
    {"tz": "Europe/Berlin", "lat_range": (47.0, 55.0), "lon_range": (5.0, 16.0)},
    {"tz": "Europe/London", "lat_range": (49.0, 61.0), "lon_range": (-10.0, 5.0)},
    {"tz": "Europe/Madrid", "lat_range": (36.0, 45.0), "lon_range": (-10.0, 5.0)},
    {"tz": "Europe/Rome", "lat_range": (36.0, 47.0), "lon_range": (6.0, 19.0)},
    {"tz": "Europe/Amsterdam", "lat_range": (50.0, 54.0), "lon_range": (2.0, 8.0)},
    {"tz": "Africa/Cairo", "lat_range": (22.0, 32.0), "lon_range": (25.0, 37.0)},
    {"tz": "Africa/Johannesburg", "lat_range": (-35.0, -22.0), "lon_range": (16.0, 36.0)},
    {"tz": "Africa/Lagos", "lat_range": (-5.0, 15.0), "lon_range": (-5.0, 15.0)},
    {"tz": "Africa/Nairobi", "lat_range": (-5.0, 6.0), "lon_range": (33.0, 42.0)},
    {"tz": "Africa/Casablanca", "lat_range": (27.0, 36.0), "lon_range": (-13.0, -1.0)},
    {"tz": "Africa/Tripoli", "lat_range": (19.0, 34.0), "lon_range": (9.0, 26.0)},
    {"tz": "America/New_York", "lat_range": (24.0, 50.0), "lon_range": (-90.0, -65.0)},
    {"tz": "America/Chicago", "lat_range": (25.0, 50.0), "lon_range": (-105.0, -85.0)},
    {"tz": "America/Denver", "lat_range": (30.0, 50.0), "lon_range": (-120.0, -100.0)},
    {"tz": "America/Los_Angeles", "lat_range": (30.0, 50.0), "lon_range": (-125.0, -105.0)},
    {"tz": "America/Toronto", "lat_range": (40.0, 55.0), "lon_range": (-90.0, -70.0)},
    {"tz": "America/Vancouver", "lat_range": (48.0, 60.0), "lon_range": (-140.0, -120.0)},
    {"tz": "America/Mexico_City", "lat_range": (14.0, 33.0), "lon_range": (-120.0, -85.0)},
    {"tz": "America/Sao_Paulo", "lat_range": (-35.0, 6.0), "lon_range": (-60.0, -30.0)},
    {"tz": "America/Buenos_Aires", "lat_range": (-56.0, -21.0), "lon_range": (-75.0, -53.0)},
]

def get_timezone_for_coordinates(lat: float, lon: float) -> str:
    """Get timezone for given coordinates"""
    for tz_data in TIMEZONE_COORDS:
        lat_range = tz_data["lat_range"]
        lon_range = tz_data["lon_range"]
        if lat_range[0] <= lat <= lat_range[1] and lon_range[0] <= lon <= lon_range[1]:
            return tz_data["tz"]
    return "UTC"

COUNTRIES_AND_CITIES = {
    "Pakistan": {
        "cities": {
            "Karachi": {"lat": 24.8607, "lon": 67.0011, "timezone": "Asia/Karachi"},
            "Lahore": {"lat": 31.5204, "lon": 74.3587, "timezone": "Asia/Karachi"},
            "Islamabad": {"lat": 33.6844, "lon": 73.0479, "timezone": "Asia/Karachi"},
            "Faisalabad": {"lat": 31.4504, "lon": 73.1350, "timezone": "Asia/Karachi"},
            "Rawalpindi": {"lat": 33.5651, "lon": 73.0169, "timezone": "Asia/Karachi"},
            "Multan": {"lat": 30.1575, "lon": 71.5249, "timezone": "Asia/Karachi"},
            "Peshawar": {"lat": 34.0151, "lon": 71.5249, "timezone": "Asia/Karachi"},
            "Quetta": {"lat": 30.1898, "lon": 67.0236, "timezone": "Asia/Karachi"},
            "Sialkot": {"lat": 32.4945, "lon": 74.5389, "timezone": "Asia/Karachi"},
            "Hyderabad": {"lat": 25.3792, "lon": 68.3667, "timezone": "Asia/Karachi"},
            "Gujranwala": {"lat": 32.1877, "lon": 74.1945, "timezone": "Asia/Karachi"},
            "Sukkur": {"lat": 27.7053, "lon": 68.8554, "timezone": "Asia/Karachi"},
            "Larkana": {"lat": 27.5582, "lon": 68.2120, "timezone": "Asia/Karachi"},
            "Bahawalpur": {"lat": 29.3956, "lon": 71.6725, "timezone": "Asia/Karachi"},
            "Sargodha": {"lat": 32.0833, "lon": 72.6667, "timezone": "Asia/Karachi"},
            "Jhang": {"lat": 31.2697, "lon": 72.3169, "timezone": "Asia/Karachi"},
            "Gujrat": {"lat": 32.5728, "lon": 74.0779, "timezone": "Asia/Karachi"},
            "Mardan": {"lat": 34.1989, "lon": 72.0289, "timezone": "Asia/Karachi"},
            "Kasur": {"lat": 31.1704, "lon": 74.4565, "timezone": "Asia/Karachi"},
        }
    },
    "India": {
        "cities": {
            "Delhi": {"lat": 28.7041, "lon": 77.1025, "timezone": "Asia/Kolkata"},
            "Mumbai": {"lat": 19.0760, "lon": 72.8777, "timezone": "Asia/Kolkata"},
            "Kolkata": {"lat": 22.5726, "lon": 88.3639, "timezone": "Asia/Kolkata"},
            "Chennai": {"lat": 13.0827, "lon": 80.2707, "timezone": "Asia/Kolkata"},
            "Bangalore": {"lat": 12.9716, "lon": 77.5946, "timezone": "Asia/Kolkata"},
            "Hyderabad": {"lat": 17.3850, "lon": 78.4867, "timezone": "Asia/Kolkata"},
            "Ahmedabad": {"lat": 23.0225, "lon": 72.5714, "timezone": "Asia/Kolkata"},
            "Jaipur": {"lat": 26.9124, "lon": 75.7873, "timezone": "Asia/Kolkata"},
            "Lucknow": {"lat": 26.8467, "lon": 80.9462, "timezone": "Asia/Kolkata"},
            "Chandigarh": {"lat": 30.7333, "lon": 76.7794, "timezone": "Asia/Kolkata"},
            "Patna": {"lat": 25.5941, "lon": 85.1376, "timezone": "Asia/Kolkata"},
            "Bhopal": {"lat": 23.2599, "lon": 77.4126, "timezone": "Asia/Kolkata"},
            "Coimbatore": {"lat": 11.0168, "lon": 76.9558, "timezone": "Asia/Kolkata"},
            "Kochi": {"lat": 9.9312, "lon": 76.2673, "timezone": "Asia/Kolkata"},
            "Varanasi": {"lat": 25.3176, "lon": 82.9739, "timezone": "Asia/Kolkata"},
            "Srinagar": {"lat": 34.0837, "lon": 74.7973, "timezone": "Asia/Kolkata"},
            "Gurgaon": {"lat": 28.4284, "lon": 77.0022, "timezone": "Asia/Kolkata"},
            "Noida": {"lat": 28.5355, "lon": 77.2100, "timezone": "Asia/Kolkata"},
            "Pune": {"lat": 18.5204, "lon": 73.8567, "timezone": "Asia/Kolkata"},
            "Surat": {"lat": 21.1702, "lon": 72.8311, "timezone": "Asia/Kolkata"},
        }
    },
    "Bangladesh": {
        "cities": {
            "Dhaka": {"lat": 23.8103, "lon": 90.4125, "timezone": "Asia/Dhaka"},
            "Chittagong": {"lat": 22.3569, "lon": 91.7832, "timezone": "Asia/Dhaka"},
            "Khulna": {"lat": 22.8200, "lon": 89.5500, "timezone": "Asia/Dhaka"},
            "Rajshahi": {"lat": 24.3745, "lon": 88.6042, "timezone": "Asia/Dhaka"},
            "Sylhet": {"lat": 24.8990, "lon": 91.8710, "timezone": "Asia/Dhaka"},
            "Barisal": {"lat": 22.7010, "lon": 90.3535, "timezone": "Asia/Dhaka"},
            "Rangpur": {"lat": 25.7439, "lon": 89.2752, "timezone": "Asia/Dhaka"},
            "Mymensingh": {"lat": 24.7471, "lon": 90.4203, "timezone": "Asia/Dhaka"},
        }
    },
    "Indonesia": {
        "cities": {
            "Jakarta": {"lat": -6.2088, "lon": 106.8456, "timezone": "Asia/Jakarta"},
            "Surabaya": {"lat": -7.2575, "lon": 112.7521, "timezone": "Asia/Jakarta"},
            "Bandung": {"lat": -6.9175, "lon": 107.6191, "timezone": "Asia/Jakarta"},
            "Medan": {"lat": 3.5952, "lon": 98.6722, "timezone": "Asia/Jakarta"},
            "Makassar": {"lat": -5.1428, "lon": 119.4128, "timezone": "Asia/Makassar"},
            "Semarang": {"lat": -6.9667, "lon": 110.4208, "timezone": "Asia/Jakarta"},
            "Palembang": {"lat": -2.9913, "lon": 104.7628, "timezone": "Asia/Jakarta"},
            "Tangerang": {"lat": -6.1783, "lon": 106.6300, "timezone": "Asia/Jakarta"},
            "Depok": {"lat": -6.4025, "lon": 106.7942, "timezone": "Asia/Jakarta"},
            "Yogyakarta": {"lat": -7.7956, "lon": 110.3695, "timezone": "Asia/Jakarta"},
        }
    },
    "Malaysia": {
        "cities": {
            "Kuala Lumpur": {"lat": 3.1390, "lon": 101.6869, "timezone": "Asia/Kuala_Lumpur"},
            "Penang": {"lat": 5.4141, "lon": 100.3288, "timezone": "Asia/Kuala_Lumpur"},
            "Johor Bahru": {"lat": 1.4927, "lon": 103.7414, "timezone": "Asia/Kuala_Lumpur"},
            "Ipoh": {"lat": 4.5975, "lon": 101.0901, "timezone": "Asia/Kuala_Lumpur"},
            "Kota Kinabalu": {"lat": 5.9804, "lon": 116.0735, "timezone": "Asia/Kuala_Lumpur"},
            "Kuching": {"lat": 1.5533, "lon": 110.3592, "timezone": "Asia/Kuala_Lumpur"},
            "Shah Alam": {"lat": 3.0733, "lon": 101.5185, "timezone": "Asia/Kuala_Lumpur"},
            "Malacca": {"lat": 2.1896, "lon": 102.2501, "timezone": "Asia/Kuala_Lumpur"},
        }
    },
    "Turkey": {
        "cities": {
            "Istanbul": {"lat": 41.0082, "lon": 28.9784, "timezone": "Europe/Istanbul"},
            "Ankara": {"lat": 39.9334, "lon": 32.8597, "timezone": "Europe/Istanbul"},
            "Izmir": {"lat": 38.4192, "lon": 27.1287, "timezone": "Europe/Istanbul"},
            "Bursa": {"lat": 40.1826, "lon": 29.0665, "timezone": "Europe/Istanbul"},
            "Antalya": {"lat": 36.8969, "lon": 30.7133, "timezone": "Europe/Istanbul"},
            "Konya": {"lat": 37.8746, "lon": 32.4932, "timezone": "Europe/Istanbul"},
            "Gaziantep": {"lat": 37.0662, "lon": 37.3833, "timezone": "Europe/Istanbul"},
            "Adana": {"lat": 37.0017, "lon": 35.3213, "timezone": "Europe/Istanbul"},
        }
    },
    "Egypt": {
        "cities": {
            "Cairo": {"lat": 30.0444, "lon": 31.2357, "timezone": "Africa/Cairo"},
            "Alexandria": {"lat": 31.2001, "lon": 29.9187, "timezone": "Africa/Cairo"},
            "Giza": {"lat": 30.0131, "lon": 31.2089, "timezone": "Africa/Cairo"},
            "Luxor": {"lat": 25.6872, "lon": 32.6396, "timezone": "Africa/Cairo"},
            "Mansoura": {"lat": 31.0409, "lon": 31.3785, "timezone": "Africa/Cairo"},
            "Tanta": {"lat": 30.7865, "lon": 31.0004, "timezone": "Africa/Cairo"},
            "Asyut": {"lat": 27.1879, "lon": 31.1685, "timezone": "Africa/Cairo"},
            "Port Said": {"lat": 31.2653, "lon": 32.3019, "timezone": "Africa/Cairo"},
        }
    },
    "Saudi Arabia": {
        "cities": {
            "Riyadh": {"lat": 24.7136, "lon": 46.6753, "timezone": "Asia/Riyadh"},
            "Jeddah": {"lat": 21.4858, "lon": 39.1925, "timezone": "Asia/Riyadh"},
            "Mecca": {"lat": 21.3891, "lon": 39.8579, "timezone": "Asia/Riyadh"},
            "Medina": {"lat": 24.5247, "lon": 39.5692, "timezone": "Asia/Riyadh"},
            "Dammam": {"lat": 26.4207, "lon": 50.0888, "timezone": "Asia/Riyadh"},
            "Khobar": {"lat": 26.2172, "lon": 50.1976, "timezone": "Asia/Riyadh"},
            "Jubail": {"lat": 27.0044, "lon": 49.6169, "timezone": "Asia/Riyadh"},
            "Taif": {"lat": 21.4373, "lon": 40.5127, "timezone": "Asia/Riyadh"},
            "Tabuk": {"lat": 28.3998, "lon": 36.5716, "timezone": "Asia/Riyadh"},
            "Abha": {"lat": 18.2154, "lon": 42.5603, "timezone": "Asia/Riyadh"},
        }
    },
    "UAE": {
        "cities": {
            "Dubai": {"lat": 25.2048, "lon": 55.2708, "timezone": "Asia/Dubai"},
            "Abu Dhabi": {"lat": 24.4539, "lon": 54.3773, "timezone": "Asia/Dubai"},
            "Sharjah": {"lat": 25.3463, "lon": 55.4209, "timezone": "Asia/Dubai"},
            "Al Ain": {"lat": 24.2075, "lon": 55.7447, "timezone": "Asia/Dubai"},
            "Ajman": {"lat": 25.4052, "lon": 55.5136, "timezone": "Asia/Dubai"},
            "Ras Al Khaimah": {"lat": 25.7895, "lon": 55.9432, "timezone": "Asia/Dubai"},
            "Fujairah": {"lat": 25.1288, "lon": 56.3265, "timezone": "Asia/Dubai"},
        }
    },
    "Qatar": {
        "cities": {
            "Doha": {"lat": 25.2854, "lon": 51.5310, "timezone": "Asia/Qatar"},
            "Al Rayyan": {"lat": 25.2919, "lon": 51.4244, "timezone": "Asia/Qatar"},
            "Al Wakrah": {"lat": 25.1592, "lon": 51.5977, "timezone": "Asia/Qatar"},
        }
    },
    "Kuwait": {
        "cities": {
            "Kuwait City": {"lat": 29.3759, "lon": 47.9774, "timezone": "Asia/Kuwait"},
            "Salmiya": {"lat": 29.3347, "lon": 48.0769, "timezone": "Asia/Kuwait"},
            "Hawally": {"lat": 29.3299, "lon": 48.0298, "timezone": "Asia/Kuwait"},
        }
    },
    "Bahrain": {
        "cities": {
            "Manama": {"lat": 26.2285, "lon": 50.5860, "timezone": "Asia/Bahrain"},
            "Muharraq": {"lat": 26.2551, "lon": 50.6083, "timezone": "Asia/Bahrain"},
        }
    },
    "Oman": {
        "cities": {
            "Muscat": {"lat": 23.5880, "lon": 58.3829, "timezone": "Asia/Muscat"},
            "Seeb": {"lat": 23.6800, "lon": 58.5500, "timezone": "Asia/Muscat"},
            "Salalah": {"lat": 17.0156, "lon": 54.0923, "timezone": "Asia/Muscat"},
        }
    },
    "United Kingdom": {
        "cities": {
            "London": {"lat": 51.5074, "lon": -0.1278, "timezone": "Europe/London"},
            "Birmingham": {"lat": 52.4862, "lon": -1.8904, "timezone": "Europe/London"},
            "Manchester": {"lat": 53.4808, "lon": -2.2426, "timezone": "Europe/London"},
            "Glasgow": {"lat": 55.8642, "lon": -4.2518, "timezone": "Europe/London"},
            "Liverpool": {"lat": 53.4084, "lon": -2.9916, "timezone": "Europe/London"},
            "Bristol": {"lat": 51.4545, "lon": -2.5879, "timezone": "Europe/London"},
            "Edinburgh": {"lat": 55.9533, "lon": -3.1883, "timezone": "Europe/London"},
            "Leeds": {"lat": 53.8008, "lon": -1.5491, "timezone": "Europe/London"},
            "Leicester": {"lat": 52.6369, "lon": -1.1398, "timezone": "Europe/London"},
            "Bradford": {"lat": 53.7960, "lon": -1.7592, "timezone": "Europe/London"},
        }
    },
    "United States": {
        "cities": {
            "New York": {"lat": 40.7128, "lon": -74.0060, "timezone": "America/New_York"},
            "Los Angeles": {"lat": 34.0522, "lon": -118.2437, "timezone": "America/Los_Angeles"},
            "Chicago": {"lat": 41.8781, "lon": -87.6298, "timezone": "America/Chicago"},
            "Houston": {"lat": 29.7604, "lon": -95.3698, "timezone": "America/Chicago"},
            "Phoenix": {"lat": 33.4484, "lon": -112.0740, "timezone": "America/Phoenix"},
            "San Francisco": {"lat": 37.7749, "lon": -122.4194, "timezone": "America/Los_Angeles"},
            "Seattle": {"lat": 47.6062, "lon": -122.3321, "timezone": "America/Los_Angeles"},
            "Denver": {"lat": 39.7392, "lon": -104.9903, "timezone": "America/Denver"},
            "Boston": {"lat": 42.3601, "lon": -71.0589, "timezone": "America/New_York"},
            "Miami": {"lat": 25.7617, "lon": -80.1918, "timezone": "America/New_York"},
            "Atlanta": {"lat": 33.7490, "lon": -84.3880, "timezone": "America/New_York"},
            "Dallas": {"lat": 32.7767, "lon": -96.7970, "timezone": "America/Chicago"},
            "San Diego": {"lat": 32.7157, "lon": -117.1611, "timezone": "America/Los_Angeles"},
            "Detroit": {"lat": 42.3314, "lon": -83.0458, "timezone": "America/Detroit"},
            "Minneapolis": {"lat": 44.9778, "lon": -93.2650, "timezone": "America/Chicago"},
        }
    },
    "Canada": {
        "cities": {
            "Toronto": {"lat": 43.6532, "lon": -79.3832, "timezone": "America/Toronto"},
            "Vancouver": {"lat": 49.2827, "lon": -123.1207, "timezone": "America/Vancouver"},
            "Montreal": {"lat": 45.5017, "lon": -73.5673, "timezone": "America/Toronto"},
            "Calgary": {"lat": 51.0447, "lon": -114.0719, "timezone": "America/Edmonton"},
            "Ottawa": {"lat": 45.4215, "lon": -75.6972, "timezone": "America/Toronto"},
            "Edmonton": {"lat": 53.5461, "lon": -113.4938, "timezone": "America/Edmonton"},
            "Winnipeg": {"lat": 49.8951, "lon": -97.1384, "timezone": "America/Winnipeg"},
            "Quebec City": {"lat": 46.8139, "lon": -71.2080, "timezone": "America/Toronto"},
        }
    },
    "Australia": {
        "cities": {
            "Sydney": {"lat": -33.8688, "lon": 151.2093, "timezone": "Australia/Sydney"},
            "Melbourne": {"lat": -37.8136, "lon": 144.9631, "timezone": "Australia/Melbourne"},
            "Brisbane": {"lat": -27.4698, "lon": 153.0251, "timezone": "Australia/Brisbane"},
            "Perth": {"lat": -31.9505, "lon": 115.8605, "timezone": "Australia/Perth"},
            "Adelaide": {"lat": -34.9285, "lon": 138.6007, "timezone": "Australia/Adelaide"},
            "Gold Coast": {"lat": -28.0167, "lon": 153.4000, "timezone": "Australia/Brisbane"},
            "Canberra": {"lat": -35.2809, "lon": 149.1300, "timezone": "Australia/Sydney"},
            "Hobart": {"lat": -42.8821, "lon": 147.3272, "timezone": "Australia/Hobart"},
        }
    },
    "Germany": {
        "cities": {
            "Berlin": {"lat": 52.5200, "lon": 13.4050, "timezone": "Europe/Berlin"},
            "Munich": {"lat": 48.1351, "lon": 11.5820, "timezone": "Europe/Berlin"},
            "Frankfurt": {"lat": 50.1109, "lon": 8.6821, "timezone": "Europe/Berlin"},
            "Hamburg": {"lat": 53.5511, "lon": 9.9937, "timezone": "Europe/Berlin"},
            "Cologne": {"lat": 50.9375, "lon": 6.9603, "timezone": "Europe/Berlin"},
            "Stuttgart": {"lat": 48.7758, "lon": 9.1829, "timezone": "Europe/Berlin"},
            "Dusseldorf": {"lat": 51.2277, "lon": 6.7735, "timezone": "Europe/Berlin"},
            "Dortmund": {"lat": 51.5136, "lon": 7.4653, "timezone": "Europe/Berlin"},
        }
    },
    "France": {
        "cities": {
            "Paris": {"lat": 48.8566, "lon": 2.3522, "timezone": "Europe/Paris"},
            "Lyon": {"lat": 45.7640, "lon": 4.8357, "timezone": "Europe/Paris"},
            "Marseille": {"lat": 43.2965, "lon": 5.3698, "timezone": "Europe/Paris"},
            "Toulouse": {"lat": 43.6047, "lon": 1.4442, "timezone": "Europe/Paris"},
            "Nice": {"lat": 43.7102, "lon": 7.2620, "timezone": "Europe/Paris"},
            "Strasbourg": {"lat": 48.5734, "lon": 7.7521, "timezone": "Europe/Paris"},
            "Montpellier": {"lat": 43.6108, "lon": 3.8767, "timezone": "Europe/Paris"},
        }
    },
    "Netherlands": {
        "cities": {
            "Amsterdam": {"lat": 52.3676, "lon": 4.9041, "timezone": "Europe/Amsterdam"},
            "Rotterdam": {"lat": 51.9244, "lon": 4.4777, "timezone": "Europe/Amsterdam"},
            "The Hague": {"lat": 52.0705, "lon": 4.3007, "timezone": "Europe/Amsterdam"},
            "Utrecht": {"lat": 52.0907, "lon": 5.1214, "timezone": "Europe/Amsterdam"},
            "Eindhoven": {"lat": 51.4416, "lon": 5.4697, "timezone": "Europe/Amsterdam"},
        }
    },
    "Belgium": {
        "cities": {
            "Brussels": {"lat": 50.8503, "lon": 4.3517, "timezone": "Europe/Brussels"},
            "Antwerp": {"lat": 51.2194, "lon": 4.4025, "timezone": "Europe/Brussels"},
            "Ghent": {"lat": 51.0543, "lon": 3.7174, "timezone": "Europe/Brussels"},
        }
    },
    "Spain": {
        "cities": {
            "Madrid": {"lat": 40.4168, "lon": -3.7038, "timezone": "Europe/Madrid"},
            "Barcelona": {"lat": 41.3851, "lon": 2.1734, "timezone": "Europe/Madrid"},
            "Valencia": {"lat": 39.4699, "lon": -0.3763, "timezone": "Europe/Madrid"},
            "Seville": {"lat": 37.3891, "lon": -5.9845, "timezone": "Europe/Madrid"},
            "Malaga": {"lat": 36.7213, "lon": -4.4214, "timezone": "Europe/Madrid"},
        }
    },
    "Italy": {
        "cities": {
            "Rome": {"lat": 41.9028, "lon": 12.4964, "timezone": "Europe/Rome"},
            "Milan": {"lat": 45.4642, "lon": 9.1900, "timezone": "Europe/Rome"},
            "Naples": {"lat": 40.8518, "lon": 14.2681, "timezone": "Europe/Rome"},
            "Turin": {"lat": 45.0703, "lon": 7.6869, "timezone": "Europe/Rome"},
            "Palermo": {"lat": 38.1157, "lon": 13.3615, "timezone": "Europe/Rome"},
        }
    },
    "South Africa": {
        "cities": {
            "Johannesburg": {"lat": -26.2041, "lon": 28.0473, "timezone": "Africa/Johannesburg"},
            "Cape Town": {"lat": -33.9249, "lon": 18.4241, "timezone": "Africa/Johannesburg"},
            "Durban": {"lat": -29.8587, "lon": 31.0218, "timezone": "Africa/Johannesburg"},
            "Pretoria": {"lat": -25.7479, "lon": 28.2293, "timezone": "Africa/Johannesburg"},
            "Port Elizabeth": {"lat": -33.9608, "lon": 25.6022, "timezone": "Africa/Johannesburg"},
        }
    },
    "Kenya": {
        "cities": {
            "Nairobi": {"lat": -1.2921, "lon": 36.8219, "timezone": "Africa/Nairobi"},
            "Mombasa": {"lat": -4.0435, "lon": 39.6682, "timezone": "Africa/Nairobi"},
            "Kisumu": {"lat": -0.1022, "lon": 34.7617, "timezone": "Africa/Nairobi"},
        }
    },
    "Nigeria": {
        "cities": {
            "Lagos": {"lat": 6.5244, "lon": 3.3792, "timezone": "Africa/Lagos"},
            "Abuja": {"lat": 9.0765, "lon": 7.3986, "timezone": "Africa/Lagos"},
            "Kano": {"lat": 12.0022, "lon": 8.5919, "timezone": "Africa/Lagos"},
            "Ibadan": {"lat": 7.3775, "lon": 3.9470, "timezone": "Africa/Lagos"},
            "Port Harcourt": {"lat": 4.7774, "lon": 7.0134, "timezone": "Africa/Lagos"},
        }
    },
    "Morocco": {
        "cities": {
            "Casablanca": {"lat": 33.5731, "lon": -7.5898, "timezone": "Africa/Casablanca"},
            "Rabat": {"lat": 34.0209, "lon": -6.8416, "timezone": "Africa/Casablanca"},
            "Marrakech": {"lat": 31.6295, "lon": -7.9811, "timezone": "Africa/Casablanca"},
            "Fes": {"lat": 34.0331, "lon": -5.0003, "timezone": "Africa/Casablanca"},
            "Tangier": {"lat": 35.7595, "lon": -5.8340, "timezone": "Africa/Casablanca"},
        }
    },
    "Iran": {
        "cities": {
            "Tehran": {"lat": 35.6892, "lon": 51.3890, "timezone": "Asia/Tehran"},
            "Mashhad": {"lat": 36.2605, "lon": 59.6168, "timezone": "Asia/Tehran"},
            "Isfahan": {"lat": 32.6546, "lon": 51.6680, "timezone": "Asia/Tehran"},
            "Karaj": {"lat": 35.7326, "lon": 50.9920, "timezone": "Asia/Tehran"},
            "Shiraz": {"lat": 29.5918, "lon": 52.5837, "timezone": "Asia/Tehran"},
            "Tabriz": {"lat": 38.0962, "lon": 46.2730, "timezone": "Asia/Tehran"},
            "Qom": {"lat": 34.6416, "lon": 50.8746, "timezone": "Asia/Tehran"},
        }
    },
    "Iraq": {
        "cities": {
            "Baghdad": {"lat": 33.3128, "lon": 44.3615, "timezone": "Asia/Baghdad"},
            "Basra": {"lat": 30.5085, "lon": 47.7803, "timezone": "Asia/Baghdad"},
            "Mosul": {"lat": 36.3363, "lon": 43.1261, "timezone": "Asia/Baghdad"},
            "Erbil": {"lat": 36.1921, "lon": 43.9865, "timezone": "Asia/Baghdad"},
            "Najaf": {"lat": 31.9966, "lon": 44.3257, "timezone": "Asia/Baghdad"},
        }
    },
    "Afghanistan": {
        "cities": {
            "Kabul": {"lat": 34.5553, "lon": 69.2075, "timezone": "Asia/Kabul"},
            "Herat": {"lat": 34.3413, "lon": 62.2038, "timezone": "Asia/Kabul"},
            "Kandahar": {"lat": 31.6089, "lon": 65.7372, "timezone": "Asia/Kabul"},
            "Mazar-i-Sharif": {"lat": 36.7090, "lon": 67.1129, "timezone": "Asia/Kabul"},
        }
    },
    "Sri Lanka": {
        "cities": {
            "Colombo": {"lat": 6.9271, "lon": 79.8612, "timezone": "Asia/Colombo"},
            "Kandy": {"lat": 7.2906, "lon": 80.6337, "timezone": "Asia/Colombo"},
            "Galle": {"lat": 6.0567, "lon": 80.2217, "timezone": "Asia/Colombo"},
        }
    },
    "Nepal": {
        "cities": {
            "Kathmandu": {"lat": 27.7172, "lon": 85.3240, "timezone": "Asia/Kathmandu"},
            "Pokhara": {"lat": 28.2096, "lon": 83.9856, "timezone": "Asia/Kathmandu"},
        }
    },
    "Myanmar": {
        "cities": {
            "Yangon": {"lat": 16.8661, "lon": 96.1951, "timezone": "Asia/Yangon"},
            "Mandalay": {"lat": 21.9588, "lon": 96.0891, "timezone": "Asia/Yangon"},
        }
    },
    "Thailand": {
        "cities": {
            "Bangkok": {"lat": 13.7563, "lon": 100.5018, "timezone": "Asia/Bangkok"},
            "Chiang Mai": {"lat": 18.7883, "lon": 98.9853, "timezone": "Asia/Bangkok"},
            "Phuket": {"lat": 7.8804, "lon": 98.3923, "timezone": "Asia/Bangkok"},
        }
    },
    "Vietnam": {
        "cities": {
            "Ho Chi Minh City": {"lat": 10.8231, "lon": 106.6297, "timezone": "Asia/Ho_Chi_Minh"},
            "Hanoi": {"lat": 21.0278, "lon": 105.8342, "timezone": "Asia/Ho_Chi_Minh"},
            "Da Nang": {"lat": 16.0544, "lon": 108.2022, "timezone": "Asia/Ho_Chi_Minh"},
        }
    },
    "Philippines": {
        "cities": {
            "Manila": {"lat": 14.5995, "lon": 120.9842, "timezone": "Asia/Manila"},
            "Quezon City": {"lat": 14.6760, "lon": 121.0437, "timezone": "Asia/Manila"},
            "Cebu": {"lat": 10.3157, "lon": 123.8854, "timezone": "Asia/Manila"},
            "Davao": {"lat": 7.0731, "lon": 125.6128, "timezone": "Asia/Manila"},
        }
    },
    "Singapore": {
        "cities": {
            "Singapore": {"lat": 1.3521, "lon": 103.8198, "timezone": "Asia/Singapore"},
        }
    },
    "Brunei": {
        "cities": {
            "Bandar Seri Begawan": {"lat": 4.9031, "lon": 114.9398, "timezone": "Asia/Brunei"},
        }
    },
    "New Zealand": {
        "cities": {
            "Auckland": {"lat": -36.8509, "lon": 174.7645, "timezone": "Pacific/Auckland"},
            "Wellington": {"lat": -41.2865, "lon": 174.7762, "timezone": "Pacific/Auckland"},
            "Christchurch": {"lat": -43.5321, "lon": 172.6306, "timezone": "Pacific/Auckland"},
        }
    },
}

# Common timezones
TIMEZONES = [
    "Asia/Karachi",
    "Asia/Kolkata",
    "Asia/Dhaka",
    "Asia/Jakarta",
    "Asia/Kuala_Lumpur",
    "Asia/Singapore",
    "Asia/Bangkok",
    "Asia/Tehran",
    "Asia/Kabul",
    "Asia/Baghdad",
    "Asia/Riyadh",
    "Asia/Dubai",
    "Asia/Muscat",
    "Asia/Qatar",
    "Asia/Kuwait",
    "Asia/Bahrain",
    "Asia/Colombo",
    "Asia/Kathmandu",
    "Asia/Yangon",
    "Europe/Istanbul",
    "Europe/Moscow",
    "Africa/Cairo",
    "Africa/Johannesburg",
    "Africa/Nairobi",
    "Africa/Lagos",
    "Africa/Casablanca",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Europe/Rome",
    "Europe/Madrid",
    "Europe/Amsterdam",
    "Europe/Brussels",
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Toronto",
    "America/Vancouver",
    "America/Mexico_City",
    "America/Sao_Paulo",
    "Australia/Sydney",
    "Australia/Melbourne",
    "Australia/Brisbane",
    "Australia/Perth",
    "Pacific/Auckland",
]

# Fiqh methods - including Hanafi, Jaffari (Shia), and Shafi
FIQH_METHODS = {
    "hanafi": {
        "name": "Hanafi",
        "asr_method": "hanafi",
        "description": "Hanafi school - uses shadow length method for Asr (later time)",
        "school": 1
    },
    "jaffari": {
        "name": "Jaffari (Shia)",
        "asr_method": "jaffari",
        "description": "Ja'fari (Shia) school - uses different calculation method",
        "school": 1
    },
    "shafi": {
        "name": "Shafi / Maliki / Hanbali",
        "asr_method": "standard",
        "description": "Standard method used by Shafi, Maliki, and Hanbali schools",
        "school": 0
    }
}
