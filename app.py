from flask import Flask, render_template, jsonify, request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherDashboard:
    def __init__(self):
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        self.weather_api_url = os.getenv('WEATHER_API_URL')
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.target_channel = os.getenv('TARGET_CHANNEL_HANDLE', '@dragonbroslegends')
    
    def get_weather(self, city, country_code=None):
        """
        Fetch weather data from OpenWeatherMap API
        """
        try:
            location = f"{city},{country_code}" if country_code else city
            params = {
                'q': location,
                'appid': self.weather_api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.weather_api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            weather_data = {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed'],
                'clouds': data['clouds']['all'],
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']),
                'timestamp': datetime.now().isoformat()
            }
            
            return weather_data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API Error: {e}")
            return None
    
    def get_youtube_channel_subscribers(self):
        """
        Fetch YouTube channel subscriber count
        """
        try:
            # Search for channel by handle
            search_url = "https://www.googleapis.com/youtube/v3/search"
            search_params = {
                'part': 'snippet',
                'q': self.target_channel,
                'type': 'channel',
                'key': self.youtube_api_key
            }
            
            search_response = requests.get(search_url, params=search_params, timeout=10)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            if search_data['items']:
                channel_id = search_data['items'][0]['snippet']['channelId']
                
                # Get channel statistics
                channel_url = "https://www.googleapis.com/youtube/v3/channels"
                channel_params = {
                    'part': 'statistics,snippet',
                    'id': channel_id,
                    'key': self.youtube_api_key
                }
                
                channel_response = requests.get(channel_url, params=channel_params, timeout=10)
                channel_response.raise_for_status()
                channel_data = channel_response.json()
                
                if channel_data['items']:
                    channel_info = channel_data['items'][0]
                    subscribers = {
                        'channel_name': channel_info['snippet']['title'],
                        'channel_id': channel_id,
                        'subscriber_count': channel_info['statistics']['subscriberCount'],
                        'view_count': channel_info['statistics']['viewCount'],
                        'video_count': channel_info['statistics']['videoCount'],
                        'channel_url': f"https://www.youtube.com/channel/{channel_id}",
                        'timestamp': datetime.now().isoformat()
                    }
                    return subscribers
            
            return None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"YouTube API Error: {e}")
            return None

# Initialize dashboard
dashboard = WeatherDashboard()

@app.route('/')
def index():
    """Render main dashboard page"""
    return render_template('index.html')

@app.route('/api/weather', methods=['GET'])
def get_weather_api():
    """API endpoint to get weather data"""
    city = request.args.get('city', 'London')
    country = request.args.get('country', '')
    
    weather_data = dashboard.get_weather(city, country)
    
    if weather_data:
        return jsonify({
            'success': True,
            'data': weather_data
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Unable to fetch weather data'
        }), 400

@app.route('/api/youtube/subscribers', methods=['GET'])
def get_youtube_subscribers():
    """API endpoint to get YouTube channel subscriber count"""
    subscribers = dashboard.get_youtube_channel_subscribers()
    
    if subscribers:
        return jsonify({
            'success': True,
            'data': subscribers
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Unable to fetch YouTube channel data'
        }), 400

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    """API endpoint to get combined dashboard data"""
    city = request.args.get('city', 'London')
    country = request.args.get('country', '')
    
    weather_data = dashboard.get_weather(city, country)
    youtube_data = dashboard.get_youtube_channel_subscribers()
    
    return jsonify({
        'weather': weather_data,
        'youtube': youtube_data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
