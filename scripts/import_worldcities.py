"""
Import cities from worldcities.csv into cities.json format.

CSV columns: city, city_ascii, lat, lng, country, iso2, iso3, admin_name, capital, population, id

This script filters cities with population > 50000 and organizes them by country.
"""
import csv
import json
from pathlib import Path
from collections import defaultdict
import pytz
from timezonefinder import TimezoneFinder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize timezone finder
tf = TimezoneFinder()

def get_timezone(lat, lon):
    """Get timezone for coordinates."""
    try:
        tz = tf.timezone_at(lat=lat, lng=lon)
        return tz if tz else "UTC"
    except Exception:
        return "UTC"

def import_cities():
    """Import cities from worldcities.csv."""
    data_dir = Path(__file__).parent.parent / "data"
    csv_file = data_dir / "worldcities.csv"
    output_file = data_dir / "cities.json"
    
    if not csv_file.exists():
        logger.error(f"CSV file not found: {csv_file}")
        return
    
    # Dictionary to store cities by country
    cities_by_country = defaultdict(lambda: {"code": "", "cities": []})
    
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        total_rows = 0
        imported = 0
        skipped_small = 0
        
        for row in reader:
            total_rows += 1
            
            try:
                city = row.get('city_ascii', '').strip()
                country = row.get('country', '').strip()
                lat = float(row.get('lat', 0))
                lon = float(row.get('lng', 0))
                iso2 = row.get('iso2', '').strip()
                population = int(float(row.get('population', 0) or 0))
                
                # Skip cities with no name or coordinates
                if not city or not country or lat == 0 or lon == 0:
                    continue
                
                # Filter: only cities with population > 50000
                if population < 50000:
                    skipped_small += 1
                    continue
                
                # Get timezone
                timezone = get_timezone(lat, lon)
                
                # Add to country
                cities_by_country[country]["code"] = iso2
                cities_by_country[country]["cities"].append({
                    "name": city,
                    "lat": round(lat, 4),
                    "lon": round(lon, 4),
                    "timezone": timezone,
                    "population": population
                })
                imported += 1
                
            except (ValueError, KeyError) as e:
                logger.debug(f"Skipping row: {e}")
                continue
    
    # Sort cities by population (descending) within each country
    for country_data in cities_by_country.values():
        country_data["cities"].sort(key=lambda x: x.get("population", 0), reverse=True)
        # Remove population from final output to reduce file size
        for city in country_data["cities"]:
            city.pop("population", None)
    
    # Sort countries alphabetically
    sorted_data = dict(sorted(cities_by_country.items()))
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Import complete!")
    logger.info(f"  Total rows in CSV: {total_rows}")
    logger.info(f"  Cities imported (pop > 50000): {imported}")
    logger.info(f"  Cities skipped (pop < 50000): {skipped_small}")
    logger.info(f"  Countries: {len(sorted_data)}")
    logger.info(f"  Output: {output_file}")
    
    # Print some stats
    print("\nTop 10 countries by city count:")
    country_counts = [(c, len(d["cities"])) for c, d in sorted_data.items()]
    country_counts.sort(key=lambda x: x[1], reverse=True)
    for country, count in country_counts[:10]:
        print(f"  {country}: {count} cities")

if __name__ == "__main__":
    import_cities()
