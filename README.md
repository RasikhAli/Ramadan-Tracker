# 🌙 Ramadan Countdown

A responsive web application for tracking Sehri (Suhoor) and Iftar times during Ramadan with multi-fiqh support, Qibla direction, and PWA capabilities.

![Ramadan Countdown](app/static/icons/icon.svg)

## ✨ Features

### 🕐 Core Features
- **Dynamic Countdown Timer** for Sehri (Fajr) and Iftar (Maghrib)
- **Real-time updates** that reset daily
- **Multi-Fiqh Support**: Hanafi, Shafi/Maliki/Hanbali, and Jaffari (Shia)

### 📐 Calculation Methods
- **Muslim World League (MWL)**
- **University of Islamic Sciences, Karachi**
- **Umm al-Qura University, Makkah**
- **Islamic Society of North America (ISNA)**

### 🌍 Location Features
- **Auto-detect location** using browser Geolocation API
- **Manual location selection** with Country/City dropdowns
- **Custom coordinates input** for precise location
- **Timezone handling** with auto-detection or manual selection

### 📅 Date Display
- **Hijri date** with automatic conversion
- **Ramadan day highlight** when in Ramadan month
- **Gregorian date** for reference

### 🧭 Qibla Direction
- **Compass display** with direction indicator
- **Distance to Kaaba** in kilometers
- **Compass direction** (N, NE, E, etc.)

### 📱 PWA Support
- **Installable** on mobile and desktop
- **Offline support** with service worker
- **Push notifications** for Sehri and Iftar reminders

### 🌐 Multi-Language
- **English**
- **اردو (Urdu)**
- **العربية (Arabic)**

### 🤲 Duas Section
Authentic duas with Arabic text, transliteration, and translation:
- Iftar Dua 1 (Sunan Abi Dawud 2358)
- Iftar Dua 2 (Sunan Abi Dawud 2357)
- Sehri Intention (with scholarly note)

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Styling**: Custom CSS with CSS Variables
- **Prayer Times API**: AlAdhan API
- **Location**: Browser Geolocation API
- **State Management**: LocalStorage

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)

## 🚀 Installation & Deployment

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/RasikhAli/Ramadan-Tracker.git
   cd Ramadan-Tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Open in browser**
   ```
   http://localhost:8000
   ```

### Production Deployment

#### Option 1: Using Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

#### Option 2: Using Uvicorn

```bash
pip install uvicorn[standard]
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Option 3: Docker

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8000
   
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Build and run**
   ```bash
   docker build -t ramadan-countdown .
   docker run -p 8000:8000 ramadan-countdown
   ```

#### Option 4: Deploy to Cloud

**Heroku:**
```bash
# Create Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port $PORT" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

**Railway/Render:**
- Connect your GitHub repository
- Set build command: `pip install -r requirements.txt`
- Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 📁 Project Structure

```
ramadan-web/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and routes
│   ├── templates/
│   │   └── index.html       # Main HTML template
│   ├── static/
│   │   ├── manifest.json    # PWA manifest
│   │   ├── sw.js           # Service worker
│   │   └── icons/
│   │       └── icon.svg    # App icon
│   ├── services/
│   │   ├── __init__.py
│   │   ├── city_service.py      # City data operations
│   │   ├── prayer_service.py    # Prayer time fetching
│   │   ├── fiqh_service.py      # Fiqh calculations
│   │   └── countdown_service.py # Countdown logic
│   └── data/
│       └── cities.py       # City data module
├── data/
│   ├── cities.json         # City coordinates and timezones
│   └── countries.json      # Country data
├── tests/
│   └── test_prayer_service.py
├── scripts/
│   └── import_cities.py    # City data import script
├── requirements.txt
├── run.py
└── README.md
```

## 🔌 API Endpoints

### Location Detection
- `GET /api/detect-location` - Detect location from timezone
- `GET /api/detect-location-from-coords` - Detect from coordinates

### City Data
- `GET /api/countries` - List all countries
- `GET /api/cities/{country}` - Get cities for a country
- `GET /api/city-data` - Get city coordinates
- `GET /api/search-city` - Search for a city

### Prayer Times
- `GET /api/prayer-times` - Get prayer times for a city
- `GET /api/prayer-times-all` - Get times for all fiqh methods
- `GET /api/prayer-times-by-coords` - Get times by coordinates

### Other
- `GET /api/hijri-date` - Get Hijri date
- `GET /api/qibla` - Get Qibla direction
- `GET /api/fiqh-methods` - Get fiqh method info
- `GET /api/health` - Health check

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

## 📝 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 8000 |
| `HOST` | Server host | 0.0.0.0 |

### Customization

- **Add more cities**: Edit `data/cities.json` or use `scripts/import_cities.py`
- **Modify calculation methods**: Edit `app/services/fiqh_service.py`
- **Change theme colors**: Edit CSS variables in `app/templates/index.html`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [AlAdhan API](https://aladhan.com/prayer-times-api) for prayer time calculations
- [GeoNames](http://www.geonames.org/) for city data
- All contributors and testers

## 📞 Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/RasikhAli/Ramadan-Tracker/issues) page.

---

**Developed with ❤️ by [Rasikh Ali](https://github.com/RasikhAli)**
