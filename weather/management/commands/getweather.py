import os
import re
import requests
import time
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings

class Command(BaseCommand):
    help = 'Get weather information for a city using OpenWeather API'

    def add_arguments(self, parser):
        parser.add_argument('city', type=str, help='City name')
        parser.add_argument(
            '--units',
            type=str,
            default='metric',
            choices=['metric', 'imperial'],
            help='Temperature units (metric=Celsius, imperial=Fahrenheit)'
        )

    def validate_city(self, city):
        """Validate city name input."""
        if not city:
            raise ValueError("City name cannot be empty")
        if not re.match(r'^[a-zA-Z\s\-]+$', city):
            raise ValueError("City name can only contain letters, spaces, and hyphens")
        return city.strip()

    def get_cached_weather(self, cache_key):
        """Get cached weather data if available."""
        return cache.get(cache_key)

    def cache_weather(self, cache_key, data):
        """Cache weather data for 10 minutes."""
        cache.set(cache_key, data, timeout=600)  # 600 seconds = 10 minutes

    def format_temperature(self, temp, units):
        """Format temperature based on units."""
        unit_symbol = '°F' if units == 'imperial' else '°C'
        return f"{temp:.1f}{unit_symbol}"

    def handle(self, *args, **options):
        try:
            city = self.validate_city(options['city'])
            units = options['units']
            api_key = os.getenv('OPENWEATHER_API_KEY')

            if not api_key:
                self.stderr.write(self.style.ERROR('Error: OPENWEATHER_API_KEY environment variable is not set'))
                return

            # Check cache first
            cache_key = f"weather_{city.lower()}_{units}"
            cached_data = self.get_cached_weather(cache_key)
            
            if cached_data:
                self.display_weather(cached_data, city, units)
                self.stdout.write(self.style.NOTICE('(Data from cache)'))
                return

            # OpenWeather API endpoint (using HTTPS)
            url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}'

            response = requests.get(url)
            
            if response.status_code == 429:  # Rate limit exceeded
                self.stderr.write(self.style.ERROR('Rate limit exceeded. Please try again later.'))
                return
                
            response.raise_for_status()
            data = response.json()

            # Cache the response
            self.cache_weather(cache_key, data)
            
            self.display_weather(data, city, units)

        except ValueError as e:
            self.stderr.write(self.style.ERROR(f'Invalid input: {str(e)}'))
        except requests.exceptions.RequestException as e:
            if 'Not Found' in str(e):
                self.stderr.write(self.style.ERROR(f'City "{city}" not found. Please check the spelling and try again.'))
            else:
                self.stderr.write(self.style.ERROR(f'Error fetching weather data: {str(e)}'))
        except KeyError as e:
            self.stderr.write(self.style.ERROR(f'Error parsing weather data: {str(e)}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Unexpected error: {str(e)}'))

    def display_weather(self, data, city, units):
        """Display formatted weather information."""
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        wind_speed = data['wind']['speed']
        wind_unit = 'mph' if units == 'imperial' else 'm/s'

        # Display weather information
        self.stdout.write('\n' + self.style.SUCCESS(f'Weather in {city.title()}:'))
        self.stdout.write(f'Temperature: {self.format_temperature(temp, units)}')
        self.stdout.write(f'Feels like: {self.format_temperature(feels_like, units)}')
        self.stdout.write(f'Humidity: {humidity}%')
        self.stdout.write(f'Conditions: {description.title()}')
        self.stdout.write(f'Wind Speed: {wind_speed} {wind_unit}\n')
