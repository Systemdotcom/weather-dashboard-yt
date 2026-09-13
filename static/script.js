// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    // Refresh every 5 minutes
    setInterval(loadDashboard, 300000);
});

async function loadDashboard() {
    const city = document.getElementById('cityInput').value || 'London';
    const country = document.getElementById('countryInput').value;
    
    try {
        const response = await fetch(`/api/dashboard?city=${city}&country=${country}`);
        const data = await response.json();
        
        if (data.weather) {
            displayWeather(data.weather);
        }
        if (data.youtube) {
            displayYoutubeData(data.youtube);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Failed to load dashboard data');
    }
}

async function searchWeather() {
    const city = document.getElementById('cityInput').value;
    if (!city.trim()) {
        alert('Please enter a city name');
        return;
    }
    
    loadDashboard();
}

function displayWeather(weatherData) {
    const weatherContent = document.getElementById('weatherContent');
    
    const iconMap = {
        '01d': '☀️', '01n': '🌙',
        '02d': '⛅', '02n': '🌙',
        '03d': '☁️', '03n': '☁️',
        '04d': '☁️', '04n': '☁️',
        '09d': '🌧️', '09n': '🌧️',
        '10d': '🌧️', '10n': '🌧️',
        '11d': '⛈️', '11n': '⛈️',
        '13d': '❄️', '13n': '❄️',
        '50d': '🌫️', '50n': '🌫️'
    };
    
    const icon = iconMap[weatherData.icon] || '🌤️';
    
    weatherContent.innerHTML = `
        <div class="weather-item">
            <div class="weather-icon">${icon}</div>
            <div class="weather-info">
                <h3>${weatherData.city}, ${weatherData.country}</h3>
                <p><strong>${Math.round(weatherData.temperature)}°C</strong></p>
                <p style="text-transform: capitalize;">${weatherData.description}</p>
            </div>
        </div>
    `;
    
    // Update detailed information
    document.getElementById('feelLike').textContent = `${Math.round(weatherData.feels_like)}°C`;
    document.getElementById('humidity').textContent = `${weatherData.humidity}%`;
    document.getElementById('windSpeed').textContent = `${weatherData.wind_speed} m/s`;
    document.getElementById('pressure').textContent = `${weatherData.pressure} hPa`;
    document.getElementById('clouds').textContent = `${weatherData.clouds}%`;
    document.getElementById('sunrise').textContent = formatTime(new Date(weatherData.sunrise));
    document.getElementById('sunset').textContent = formatTime(new Date(weatherData.sunset));
    document.getElementById('lastUpdate').textContent = formatDateTime(new Date(weatherData.timestamp));
}

function displayYoutubeData(youtubeData) {
    const youtubeContent = document.getElementById('youtubeContent');
    
    const subscriberCount = formatNumberWithCommas(youtubeData.subscriber_count);
    const viewCount = formatNumberWithCommas(youtubeData.view_count);
    const videoCount = youtubeData.video_count;
    
    youtubeContent.innerHTML = `
        <div class="youtube-item">
            <label>📺 Channel Name</label>
            <value>${youtubeData.channel_name}</value>
        </div>
        <div class="youtube-item">
            <label>👥 Subscribers</label>
            <value>${subscriberCount}</value>
        </div>
        <div class="youtube-item">
            <label>👀 Total Views</label>
            <value>${viewCount}</value>
        </div>
        <div class="youtube-item">
            <label>🎥 Videos</label>
            <value>${videoCount}</value>
        </div>
        <a href="${youtubeData.channel_url}" target="_blank" class="channel-link">
            Visit Channel →
        </a>
    `;
}

function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function formatDateTime(date) {
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatNumberWithCommas(num) {
    if (num === 'unlisted' || !num) return 'N/A';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function showError(message) {
    const weatherContent = document.getElementById('weatherContent');
    const youtubeContent = document.getElementById('youtubeContent');
    
    weatherContent.innerHTML = `<p style="color: red;">${message}</p>`;
    youtubeContent.innerHTML = `<p style="color: red;">${message}</p>`;
}

// Allow Enter key to search
document.addEventListener('DOMContentLoaded', function() {
    const cityInput = document.getElementById('cityInput');
    if (cityInput) {
        cityInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchWeather();
            }
        });
    }
});
