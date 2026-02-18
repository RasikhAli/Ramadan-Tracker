"""
Offline Data Import Script for World Cities
Uses GeoNames cities15000.zip (cities with population > 15000)

This script generates:
- data/countries.json - List of countries sorted alphabetically
- data/cities.json - City data with country, name, lat, lon, timezone

Run this script once to generate the data files.
"""
import json
import os
import zipfile
import urllib.request
import csv
import logging
from typing import Dict, List, Set
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# GeoNames data URL
GEONAMES_URL = "https://download.geonames.org/export/dump/cities15000.zip"
GEONAMES_FILE = "cities15000.txt"

# Output files
OUTPUT_DIR = "data"
COUNTRIES_FILE = os.path.join(OUTPUT_DIR, "countries.json")
CITIES_FILE = os.path.join(OUTPUT_DIR, "cities.json")

# GeoNames column indices
GEONAMES_COLUMNS = {
    'geonameid': 0,
    'name': 1,
    'asciiname': 2,
    'alternatenames': 3,
    'latitude': 4,
    'longitude': 5,
    'feature_class': 6,
    'feature_code': 7,
    'country_code': 8,
    'cc2': 9,
    'admin1_code': 10,
    'admin2_code': 11,
    'admin3_code': 12,
    'admin4_code': 13,
    'population': 14,
    'elevation': 15,
    'dem': 16,
    'timezone': 17,
    'modification_date': 18,
}

# Country code to name mapping (ISO 3166-1 alpha-2)
COUNTRY_NAMES = {
    'AF': 'Afghanistan', 'AL': 'Albania', 'DZ': 'Algeria', 'AD': 'Andorra',
    'AO': 'Angola', 'AG': 'Antigua and Barbuda', 'AR': 'Argentina', 'AM': 'Armenia',
    'AU': 'Australia', 'AT': 'Austria', 'AZ': 'Azerbaijan', 'BS': 'Bahamas',
    'BH': 'Bahrain', 'BD': 'Bangladesh', 'BB': 'Barbados', 'BY': 'Belarus',
    'BE': 'Belgium', 'BZ': 'Belize', 'BJ': 'Benin', 'BT': 'Bhutan',
    'BO': 'Bolivia', 'BA': 'Bosnia and Herzegovina', 'BW': 'Botswana', 'BR': 'Brazil',
    'BN': 'Brunei', 'BG': 'Bulgaria', 'BF': 'Burkina Faso', 'BI': 'Burundi',
    'CV': 'Cabo Verde', 'KH': 'Cambodia', 'CM': 'Cameroon', 'CA': 'Canada',
    'CF': 'Central African Republic', 'TD': 'Chad', 'CL': 'Chile', 'CN': 'China',
    'CO': 'Colombia', 'KM': 'Comoros', 'CG': 'Congo', 'CR': 'Costa Rica',
    'CI': 'Côte d\'Ivoire', 'HR': 'Croatia', 'CU': 'Cuba', 'CY': 'Cyprus',
    'CZ': 'Czechia', 'DK': 'Denmark', 'DJ': 'Djibouti', 'DM': 'Dominica',
    'DO': 'Dominican Republic', 'EC': 'Ecuador', 'EG': 'Egypt', 'SV': 'El Salvador',
    'GQ': 'Equatorial Guinea', 'ER': 'Eritrea', 'EE': 'Estonia', 'SZ': 'Eswatini',
    'ET': 'Ethiopia', 'FJ': 'Fiji', 'FI': 'Finland', 'FR': 'France',
    'GA': 'Gabon', 'GM': 'Gambia', 'GE': 'Georgia', 'DE': 'Germany',
    'GH': 'Ghana', 'GR': 'Greece', 'GD': 'Grenada', 'GT': 'Guatemala',
    'GN': 'Guinea', 'GW': 'Guinea-Bissau', 'GY': 'Guyana', 'HT': 'Haiti',
    'HN': 'Honduras', 'HU': 'Hungary', 'IS': 'Iceland', 'IN': 'India',
    'ID': 'Indonesia', 'IR': 'Iran', 'IQ': 'Iraq', 'IE': 'Ireland',
    'IL': 'Israel', 'IT': 'Italy', 'JM': 'Jamaica', 'JP': 'Japan',
    'JO': 'Jordan', 'KZ': 'Kazakhstan', 'KE': 'Kenya', 'KI': 'Kiribati',
    'KP': 'North Korea', 'KR': 'South Korea', 'KW': 'Kuwait', 'KG': 'Kyrgyzstan',
    'LA': 'Laos', 'LV': 'Latvia', 'LB': 'Lebanon', 'LS': 'Lesotho',
    'LR': 'Liberia', 'LY': 'Libya', 'LI': 'Liechtenstein', 'LT': 'Lithuania',
    'LU': 'Luxembourg', 'MG': 'Madagascar', 'MW': 'Malawi', 'MY': 'Malaysia',
    'MV': 'Maldives', 'ML': 'Mali', 'MT': 'Malta', 'MH': 'Marshall Islands',
    'MR': 'Mauritania', 'MU': 'Mauritius', 'MX': 'Mexico', 'FM': 'Micronesia',
    'MD': 'Moldova', 'MC': 'Monaco', 'MN': 'Mongolia', 'ME': 'Montenegro',
    'MA': 'Morocco', 'MZ': 'Mozambique', 'MM': 'Myanmar', 'NA': 'Namibia',
    'NR': 'Nauru', 'NP': 'Nepal', 'NL': 'Netherlands', 'NZ': 'New Zealand',
    'NI': 'Nicaragua', 'NE': 'Niger', 'NG': 'Nigeria', 'MK': 'North Macedonia',
    'NO': 'Norway', 'OM': 'Oman', 'PK': 'Pakistan', 'PW': 'Palau',
    'PS': 'Palestine', 'PA': 'Panama', 'PG': 'Papua New Guinea', 'PY': 'Paraguay',
    'PE': 'Peru', 'PH': 'Philippines', 'PL': 'Poland', 'PT': 'Portugal',
    'QA': 'Qatar', 'RO': 'Romania', 'RU': 'Russia', 'RW': 'Rwanda',
    'KN': 'Saint Kitts and Nevis', 'LC': 'Saint Lucia', 'VC': 'Saint Vincent and the Grenadines',
    'WS': 'Samoa', 'SM': 'San Marino', 'ST': 'Sao Tome and Principe', 'SA': 'Saudi Arabia',
    'SN': 'Senegal', 'RS': 'Serbia', 'SC': 'Seychelles', 'SL': 'Sierra Leone',
    'SG': 'Singapore', 'SK': 'Slovakia', 'SI': 'Slovenia', 'SB': 'Solomon Islands',
    'SO': 'Somalia', 'ZA': 'South Africa', 'SS': 'South Sudan', 'ES': 'Spain',
    'LK': 'Sri Lanka', 'SD': 'Sudan', 'SR': 'Suriname', 'SE': 'Sweden',
    'CH': 'Switzerland', 'SY': 'Syria', 'TW': 'Taiwan', 'TJ': 'Tajikistan',
    'TZ': 'Tanzania', 'TH': 'Thailand', 'TL': 'Timor-Leste', 'TG': 'Togo',
    'TO': 'Tonga', 'TT': 'Trinidad and Tobago', 'TN': 'Tunisia', 'TR': 'Turkey',
    'TM': 'Turkmenistan', 'TV': 'Tuvalu', 'UG': 'Uganda', 'UA': 'Ukraine',
    'AE': 'UAE', 'GB': 'United Kingdom', 'US': 'United States', 'UY': 'Uruguay',
    'UZ': 'Uzbekistan', 'VU': 'Vanuatu', 'VA': 'Vatican City', 'VE': 'Venezuela',
    'VN': 'Vietnam', 'YE': 'Yemen', 'ZM': 'Zambia', 'ZW': 'Zimbabwe',
    # Additional codes
    'XK': 'Kosovo', 'EH': 'Western Sahara', 'AX': 'Åland Islands',
}

# Priority countries for Ramadan app (Muslim-majority and relevant countries)
PRIORITY_COUNTRIES = {
    'AF', 'BH', 'BD', 'DJ', 'EG', 'ID', 'IR', 'IQ', 'JO', 'KW',
    'LB', 'LY', 'MY', 'MV', 'MR', 'MA', 'OM', 'PK', 'PS', 'QA',
    'SA', 'SO', 'SD', 'SY', 'TN', 'TR', 'AE', 'YE', 'AL', 'AZ',
    'BJ', 'BF', 'CM', 'TD', 'KM', 'GM', 'GN', 'GW', 'ER', 'ET',
    'GA', 'GH', 'GN', 'IN', 'KZ', 'KG', 'ML', 'NE', 'NG', 'SN',
    'SL', 'TJ', 'TM', 'UG', 'UZ', 'EH', 'XK'
}


def download_geonames_data():
    """Download GeoNames cities data."""
    logger.info(f"Downloading GeoNames data from {GEONAMES_URL}")
    
    zip_path = "cities15000.zip"
    
    try:
        urllib.request.urlretrieve(GEONAMES_URL, zip_path)
        logger.info(f"Downloaded {zip_path}")
        
        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        logger.info(f"Extracted {GEONAMES_FILE}")
        
        # Clean up zip file
        os.remove(zip_path)
        logger.info("Cleaned up zip file")
        
        return True
    except Exception as e:
        logger.error(f"Error downloading GeoNames data: {e}")
        return False


def parse_geonames_data() -> Dict[str, List[Dict]]:
    """Parse GeoNames data and organize by country."""
    cities_by_country = defaultdict(list)
    
    logger.info(f"Parsing {GEONAMES_FILE}")
    
    with open(GEONAMES_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        
        for row in reader:
            try:
                country_code = row[GEONAMES_COLUMNS['country_code']]
                city_name = row[GEONAMES_COLUMNS['asciiname']] or row[GEONAMES_COLUMNS['name']]
                latitude = float(row[GEONAMES_COLUMNS['latitude']])
                longitude = float(row[GEONAMES_COLUMNS['longitude']])
                timezone = row[GEONAMES_COLUMNS['timezone']]
                population = int(row[GEONAMES_COLUMNS['population']]) if row[GEONAMES_COLUMNS['population']] else 0
                
                # Skip if no valid timezone
                if not timezone or timezone == '':
                    continue
                
                city_data = {
                    'name': city_name,
                    'lat': latitude,
                    'lon': longitude,
                    'timezone': timezone,
                    'population': population,
                }
                
                cities_by_country[country_code].append(city_data)
                
            except (ValueError, IndexError) as e:
                continue
    
    logger.info(f"Parsed {sum(len(cities) for cities in cities_by_country.values())} cities from {len(cities_by_country)} countries")
    
    return cities_by_country


def generate_output_files(cities_by_country: Dict[str, List[Dict]]):
    """Generate countries.json and cities.json files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate countries list (sorted alphabetically)
    country_codes = set(cities_by_country.keys())
    countries = []
    
    for code in country_codes:
        name = COUNTRY_NAMES.get(code, code)
        countries.append({
            'code': code,
            'name': name,
        })
    
    # Sort countries alphabetically by name
    countries.sort(key=lambda x: x['name'])
    
    # Write countries.json
    with open(COUNTRIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(countries, f, indent=2, ensure_ascii=False)
    logger.info(f"Generated {COUNTRIES_FILE} with {len(countries)} countries")
    
    # Generate cities.json
    cities_output = {}
    
    for country_code, cities in cities_by_country.items():
        country_name = COUNTRY_NAMES.get(country_code, country_code)
        
        # Sort cities alphabetically by name
        cities.sort(key=lambda x: x['name'])
        
        # Remove population from output (not needed for app)
        cities_clean = []
        seen_names = set()
        
        for city in cities:
            # Handle duplicate city names by adding region suffix
            city_name = city['name']
            if city_name in seen_names:
                continue  # Skip duplicates
            
            seen_names.add(city_name)
            cities_clean.append({
                'name': city['name'],
                'lat': city['lat'],
                'lon': city['lon'],
                'timezone': city['timezone'],
            })
        
        cities_output[country_name] = {
            'code': country_code,
            'cities': cities_clean,
        }
    
    # Write cities.json
    with open(CITIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(cities_output, f, indent=2, ensure_ascii=False)
    logger.info(f"Generated {CITIES_FILE} with cities from {len(cities_output)} countries")


def cleanup():
    """Clean up temporary files."""
    if os.path.exists(GEONAMES_FILE):
        os.remove(GEONAMES_FILE)
        logger.info(f"Cleaned up {GEONAMES_FILE}")


def main():
    """Main entry point."""
    logger.info("Starting data import...")
    
    # Download GeoNames data
    if not download_geonames_data():
        logger.error("Failed to download GeoNames data")
        return
    
    # Parse the data
    cities_by_country = parse_geonames_data()
    
    # Generate output files
    generate_output_files(cities_by_country)
    
    # Clean up
    cleanup()
    
    logger.info("Data import complete!")


if __name__ == "__main__":
    main()