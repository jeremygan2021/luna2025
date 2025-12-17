import React, { useState, useEffect } from 'react';
import { MacWindow } from '../MacWindow';

interface WeatherData {
  temperature: number;
  windspeed: number;
  weathercode: number;
}

interface WeatherAppProps {
  onClose: () => void;
}

export const WeatherApp: React.FC<WeatherAppProps> = ({ onClose }) => {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Coordinates for Cupertino (Apple HQ)
    const lat = 37.33;
    const long = -122.03;
    
    fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${long}&current_weather=true`)
      .then(res => res.json())
      .then(data => {
        setWeather({
          temperature: data.current_weather.temperature,
          windspeed: data.current_weather.windspeed,
          weathercode: data.current_weather.weathercode
        });
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError('Failed to fetch weather');
        setLoading(false);
      });
  }, []);

  // Simple WMO code interpretation
  const getWeatherIcon = (code: number) => {
    if (code === 0) return '☀️'; // Clear sky
    if (code >= 1 && code <= 3) return '⛅'; // Cloudy
    if (code >= 45 && code <= 48) return '🌫️'; // Fog
    if (code >= 51 && code <= 67) return '🌧️'; // Drizzle/Rain
    if (code >= 71 && code <= 77) return '❄️'; // Snow
    if (code >= 95) return '⛈️'; // Thunderstorm
    return '❓';
  };

  const getWeatherDesc = (code: number) => {
    if (code === 0) return 'Clear sky';
    if (code >= 1 && code <= 3) return 'Partly cloudy';
    if (code >= 45 && code <= 48) return 'Foggy';
    if (code >= 51 && code <= 67) return 'Raining';
    if (code >= 71 && code <= 77) return 'Snowing';
    if (code >= 95) return 'Thunderstorm';
    return 'Unknown';
  };

  return (
    <MacWindow title="Weather" onClose={onClose}>
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <h3 style={{ margin: '0 0 10px 0', textTransform: 'uppercase' }}>Cupertino, CA</h3>
        
        {loading && <div>Loading satellite data...</div>}
        {error && <div style={{ color: 'red' }}>{error}</div>}
        
        {weather && (
          <div>
            <div style={{ fontSize: '64px', margin: '20px 0' }}>
              {getWeatherIcon(weather.weathercode)}
            </div>
            <div style={{ fontSize: '32px', fontWeight: 'bold' }}>
              {weather.temperature}°C
            </div>
            <div style={{ marginTop: '10px', fontSize: '18px' }}>
              {getWeatherDesc(weather.weathercode)}
            </div>
            <div style={{ marginTop: '20px', fontSize: '14px', borderTop: '1px dashed black', paddingTop: '10px' }}>
              Wind: {weather.windspeed} km/h
            </div>
          </div>
        )}
      </div>
    </MacWindow>
  );
};
