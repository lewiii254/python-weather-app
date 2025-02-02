# Weather Project

A Django-based weather information application that fetches weather data from OpenWeather API.

## Setup

1. Clone the repository
```bash
git clone <repository-url>
cd weather-project
```

2. Create a virtual environment and activate it
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a .env file in the project root with the following variables:
```
OPENWEATHER_API_KEY=your_api_key_here
DJANGO_SECRET_KEY=your_django_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. Run migrations
```bash
python manage.py migrate
```

## Usage

To get weather information for a city:
```bash
python manage.py getweather "city name" [--units metric|imperial]
```

Examples:
```bash
# Get weather in Celsius (default)
python manage.py getweather "London"

# Get weather in Fahrenheit
python manage.py getweather "New York" --units imperial
```

Features:
- Temperature in both Celsius (metric) and Fahrenheit (imperial)
- Feels-like temperature
- Humidity percentage
- Weather conditions
- Wind speed (m/s for metric, mph for imperial)
- Response caching (10-minute cache to avoid repeated API calls)
- Input validation for city names
- Detailed error messages

## Security Notes

- Never commit the .env file to version control
- Keep your API keys and secret keys secure
- In production, set DEBUG=False and configure ALLOWED_HOSTS appropriately
