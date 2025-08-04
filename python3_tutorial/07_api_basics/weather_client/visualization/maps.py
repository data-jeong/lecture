import folium
from typing import List, Tuple, Optional, Dict, Any
import json
from pathlib import Path
from ..models.location import Location
from ..models.weather import Weather


class WeatherMap:
    def __init__(self, center: Tuple[float, float] = (37.5665, 126.9780),
                 zoom_start: int = 10):
        self.center = center
        self.zoom_start = zoom_start
        self.map = None
        
    def create_map(self) -> folium.Map:
        self.map = folium.Map(
            location=self.center,
            zoom_start=self.zoom_start,
            tiles='OpenStreetMap'
        )
        
        folium.TileLayer('CartoDB positron').add_to(self.map)
        folium.TileLayer('CartoDB dark_matter').add_to(self.map)
        folium.LayerControl().add_to(self.map)
        
        return self.map
        
    def add_weather_marker(self, weather: Weather) -> None:
        if not self.map:
            self.create_map()
            
        location = weather.location
        current = weather.current
        
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <h4>{location.name}, {location.country}</h4>
            <p><b>Temperature:</b> {current.temperature:.1f}°C</p>
            <p><b>Feels Like:</b> {current.feels_like:.1f}°C</p>
            <p><b>Weather:</b> {current.description}</p>
            <p><b>Humidity:</b> {current.humidity}%</p>
            <p><b>Wind:</b> {current.wind_speed:.1f} m/s</p>
            <p><b>Pressure:</b> {current.pressure} hPa</p>
        </div>
        """
        
        icon_color = self._get_temperature_color(current.temperature)
        
        folium.Marker(
            location=[location.latitude, location.longitude],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{location.name}: {current.temperature:.1f}°C",
            icon=folium.Icon(color=icon_color, icon='cloud')
        ).add_to(self.map)
        
    def add_multiple_weather_markers(self, weather_list: List[Weather]) -> None:
        if not self.map:
            self.create_map()
            
        for weather in weather_list:
            self.add_weather_marker(weather)
            
    def add_temperature_heatmap(self, weather_data: List[Dict[str, Any]]) -> None:
        if not self.map:
            self.create_map()
            
        try:
            from folium.plugins import HeatMap
            
            heat_data = []
            for data in weather_data:
                lat = data.get('latitude')
                lon = data.get('longitude')
                temp = data.get('temperature', 0)
                
                if lat and lon:
                    heat_data.append([lat, lon, temp])
                    
            if heat_data:
                HeatMap(heat_data, name='Temperature Heatmap').add_to(self.map)
                
        except ImportError:
            print("folium.plugins not available, skipping heatmap")
            
    def add_wind_arrows(self, weather_list: List[Weather]) -> None:
        if not self.map:
            self.create_map()
            
        for weather in weather_list:
            location = weather.location
            current = weather.current
            
            start_point = [location.latitude, location.longitude]
            
            end_lat, end_lon = self._calculate_wind_endpoint(
                location.latitude, location.longitude,
                current.wind_direction, current.wind_speed
            )
            end_point = [end_lat, end_lon]
            
            color = self._get_wind_color(current.wind_speed)
            
            folium.PolyLine(
                locations=[start_point, end_point],
                color=color,
                weight=2 + current.wind_speed / 5,
                opacity=0.8,
                tooltip=f"Wind: {current.wind_speed:.1f} m/s"
            ).add_to(self.map)
            
    def add_circle_marker(self, location: Location, radius: float = 10000,
                         color: str = 'blue', fill: bool = True) -> None:
        if not self.map:
            self.create_map()
            
        folium.Circle(
            location=[location.latitude, location.longitude],
            radius=radius,
            color=color,
            fill=fill,
            fillColor=color,
            fillOpacity=0.3,
            popup=f"{location.name}, {location.country}",
            tooltip=location.name
        ).add_to(self.map)
        
    def add_weather_layer(self, layer_type: str = 'temperature') -> None:
        if not self.map:
            self.create_map()
            
        if layer_type == 'temperature':
            layer_url = 'https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid={api_key}'
        elif layer_type == 'precipitation':
            layer_url = 'https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid={api_key}'
        elif layer_type == 'clouds':
            layer_url = 'https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid={api_key}'
        elif layer_type == 'wind':
            layer_url = 'https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid={api_key}'
        else:
            return
            
        folium.TileLayer(
            tiles=layer_url,
            attr='OpenWeatherMap',
            name=f'{layer_type.capitalize()} Layer',
            overlay=True,
            control=True,
            opacity=0.6
        ).add_to(self.map)
        
    def add_search_control(self) -> None:
        if not self.map:
            self.create_map()
            
        try:
            from folium.plugins import Search
            
            search = Search(
                layer=self.map,
                search_label='name',
                search_zoom=12,
                position='topright'
            )
            self.map.add_child(search)
            
        except ImportError:
            print("Search plugin not available")
            
    def save_map(self, filename: str = 'weather_map.html') -> None:
        if self.map:
            self.map.save(filename)
            print(f"Map saved as {filename}")
        else:
            print("No map to save. Create a map first.")
            
    def _get_temperature_color(self, temperature: float) -> str:
        if temperature < 0:
            return 'blue'
        elif temperature < 10:
            return 'lightblue'
        elif temperature < 20:
            return 'green'
        elif temperature < 30:
            return 'orange'
        else:
            return 'red'
            
    def _get_wind_color(self, wind_speed: float) -> str:
        if wind_speed < 2:
            return 'green'
        elif wind_speed < 5:
            return 'yellow'
        elif wind_speed < 8:
            return 'orange'
        else:
            return 'red'
            
    def _calculate_wind_endpoint(self, lat: float, lon: float,
                                direction: float, speed: float) -> Tuple[float, float]:
        import math
        
        scale = speed * 0.01
        
        direction_rad = math.radians(direction)
        
        delta_lat = scale * math.cos(direction_rad)
        delta_lon = scale * math.sin(direction_rad) / math.cos(math.radians(lat))
        
        end_lat = lat + delta_lat
        end_lon = lon + delta_lon
        
        return end_lat, end_lon
        
    def create_comparison_map(self, weather_list: List[Weather]) -> folium.Map:
        if not weather_list:
            return self.create_map()
            
        lats = [w.location.latitude for w in weather_list]
        lons = [w.location.longitude for w in weather_list]
        
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        self.center = (center_lat, center_lon)
        self.create_map()
        
        for weather in weather_list:
            self.add_weather_marker(weather)
            
        bounds = [[min(lats), min(lons)], [max(lats), max(lons)]]
        self.map.fit_bounds(bounds)
        
        return self.map