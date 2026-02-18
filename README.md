# Ramadan Sehri & Iftar Tracker 🌙

A modern, responsive web application for tracking Sehri and Iftar times during Ramadan with multi-fiqh support. Built with FastAPI and vanilla HTML/CSS/JS.

![Ramadan Countdown](https://img.shields.io/badge/Ramadan-2026-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### Multi-Fiqh Countdown
- **Compare prayer times across three Islamic schools of jurisprudence:**
  - Hanafi
  - Shafi / Maliki / Hanbali
  - Jaffari (Shia)
- Side-by-side display of Sehri end times and Iftar times for each method
- Visual color-coding: Green (Hanafi), Purple (Shafi), Pink (Jaffari)

### Smart Location Detection
- Auto-detect user location via browser timezone and IP geolocation
- Manual country/city/timezone selection
- Support for 39+ countries and 200+ cities worldwide
- Search functionality to quickly find any city

### Prayer Times
- Uses the Aladhan API for reliable prayer time calculations
- Different calculation methods for each fiqh:
  - Hanafi: Later Asr time (shadow length method)
  - Jaffari: Earlier Fajr, later Iftar (+10 minutes)
  - Shafi/Maliki/Hanbali: Standard calculation
- Toggle between 12-hour (AM/PM) and 24-hour formats

### Beautiful Duas Section
- **Two authentic Iftar duas** with:
  - Arabic text (elegant Amiri font)
  - English meaning
  - Transliteration
  - Source references (Sunan Abi Dawud)
- **One Sehri intention dua** with scholarly note about niyyah
- Copy-to-clipboard functionality
- Expandable card design

### Modern UI/UX
- **Calm, spiritual aesthetic** with deep navy/gold color palette
- Glassmorphism card effects with backdrop blur
- Animated starfield background
- Dark/Light theme toggle with smooth transitions
- Responsive design for mobile, tablet, and desktop
- Ultra-wide screen support (up to 1400px max-width)
- Thumb-friendly buttons and large tap targets
- WCAG-compliant accessibility features

## 🚀 What's New in This Version

### Multi-Fiqh Countdown Logic
- **Display Order:** Jaffari → Hanafi → Shafi (for easy comparison)
- **Timezone-Aware Countdown:** All countdowns properly handle timezone differences
- **Fixed NaN Bug:** Countdown timers now properly validate time values
- **Iftar Times:** Jaffari method shows +10 minutes for Maghrib as per Shia fiqh

### UI/UX Improvements
- ✅ New project title: "Ramadan Sehri & Iftar Tracker"
- ✅ Enhanced light mode with warm cream/gold gradients
- ✅ Lantern motifs in light mode (replaces stars)
- ✅ Improved typography and contrast in light mode
- ✅ Smooth toggle transition between dark/light themes
- ✅ Multi-fiqh comparison view (Jaffari → Hanafi → Shafi)
- ✅ Real-time countdown timers for all three methods
- ✅ Enhanced duas section with English meanings
- ✅ Animated starfield background (dark) / lantern glow (light)
- ✅ Improved mobile responsiveness
- ✅ Sticky countdown on mobile devices
- ✅ Copy-to-clipboard for duas
- ✅ Glassmorphism card effects
- ✅ Responsive layout (mobile → desktop → ultrawide)

## 📱 Supported Regions

### Countries Include:
- Pakistan, India, Bangladesh, Indonesia, Malaysia
- Saudi Arabia, UAE, Qatar, Kuwait, Bahrain, Oman
- Turkey, Egypt, Morocco, Nigeria, Kenya, South Africa
- United Kingdom, United States, Canada, Australia
- Germany, France, Netherlands, Belgium, Spain, Italy
- And many more...

### Timezones
All major timezones supported with automatic DST handling.

## 🕰️ Multi-Fiqh Countdown Explanation

Different Islamic schools of jurisprudence (madhabs) have slightly different methods for calculating prayer times:

| School | Fajr | Asr | Maghrib (Iftar) |
|--------|------|-----|-----------------|
| **Hanafi** | Standard | Later (shadow length) | Standard |
| **Shafi/Maliki/Hanbali** | Standard | Standard | Standard |
| **Jaffari (Shia)** | ~20 min earlier | Later | +10 min |

This app displays all three methods side-by-side so you can choose the timing that follows your school's methodology.

## 📊 Calculation Methods Note

The prayer times are calculated using the Aladhan API with the following parameters:

| Fiqh Method | Calculation Method | School | Fajr Angle | Maghrib Angle |
|-------------|-------------------|--------|------------|---------------|
| Hanafi | 2 (Muslim World League) | 1 (Hanafi) | 18° | 18° (+18 min) |
| Shafi/Maliki/Hanbali | 2 (Muslim World League) | 0 (Standard) | 18° | 18° |
| Jaffari (Shia) | 8 (Institute of Geophysics, Tehran) | 1 (Jaffari) | 16° | 14° (+10 min) |

**Note:** The Jaffari Iftar time includes an explicit +10 minute adjustment as per Shia fiqh practice.

## 🤲 Duas Displayed in App

### Iftar Duas

**Dua 1 (Authentic)**
> اللَّهُمَّ إِنِّي لَكَ صُمْتُ وَبِكَ آمَنْتُ وَعَلَىٰ رِزْقِكَ أَفْطَرْتُ

*Meaning:* O Allah, I fasted for You and believed in You and I break my fast with Your sustenance.

*Source:* Sunan Abi Dawud (2358)

**Dua 2 (Authentic)**
> ذَهَبَ الظَّمَأُ، وَابْتَلَّتِ الْعُرُوقُ، وَثَبَتَ الأَجْرُ إِنْ شَاءَ اللَّهُ

*Meaning:* The thirst is gone, the veins are moist, and the reward is established, insha'Allah.

*Source:* Sunan Abi Dawud (2357)

### Sehri Intention

> وَبِصَوْمِ غَدٍ نَّوَيْتُ مِنْ شَهْرِ رَمَضَانَ

*Meaning:* I intend to fast tomorrow in the month of Ramadan.

*Note:* The intention (niyyah) for fasting is an action of the heart. Scholars agree it should be made before the time of Sehri ends, but verbal recitation is optional. The intention need not be spoken aloud.

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ramadan-web
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
# or
python run.py
```

5. Open browser:
```
http://localhost:8000
```

## 📁 Project Structure

```
ramadan-web/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI backend
│   ├── api/              # API routes (if needed)
│   ├── data/
│   │   ├── __init__.py
│   │   └── cities.py     # City/timezone data
│   ├── static/           # Static files
│   └── templates/
│       └── index.html    # Frontend UI
├── requirements.txt
├── run.py
└── README.md
```

## 🎨 Design System

### Colors
| Purpose | Light Mode | Dark Mode |
|---------|------------|-----------|
| Background | #fefcf8 (warm cream) | #0f1729 |
| Card | #ffffff | #1a2744 |
| Primary (Gold) | #f0c14b | #f0c14b |
| Sehri (Blue) | #60a5fa | #60a5fa |
| Iftar (Amber) | #fbbf24 | #fbbf24 |
| Hanafi (Green) | #34d399 | #34d399 |
| Shafi (Purple) | #a78bfa | #a78bfa |
| Jaffari (Pink) | #f472b6 | #f472b6 |

### Light Mode Features
- Warm cream background with subtle gold gradients
- Soft lantern motifs in place of stars
- Gentle shadows for depth
- Maintained color consistency for fiqh methods
- Smooth theme toggle transition

### Typography
- **UI Text:** DM Sans (Google Fonts)
- **Arabic Text:** Amiri (Google Fonts)

### Layout
- Mobile-first responsive design
- CSS Grid for complex layouts
- Flexbox for component alignment
- CSS Variables for theming
- Glassmorphism effects

## 🔧 API Endpoints

| Endpoint | Description |
|-----------|-------------|
| `GET /` | Main page |
| `GET /api/detect-location` | Auto-detect location |
| `GET /api/datas` | Get all countries/cities/timezones |
| `GET /api/search-city` | Search for a city |
| `GET /api/prayer-times` | Get prayer times for one method |
| `GET /api/prayer-times-all` | Get prayer times for all three methods |

## 📱 Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👤 Developer

- **GitHub:** [RasikhAli](https://github.com/RasikhAli)
- **LinkedIn:** [Rasikh Ali](https://www.linkedin.com/in/rasikh-ali/)
- **Repository:** [Ramadan-Tracker](https://github.com/RasikhAli/Ramadan-Tracker)

## 📄 License

This project is licensed under the MIT License.

---

*May Allah accept our fasting and prayers during Ramadan. Ameen.* 🤲🌙
