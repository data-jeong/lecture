import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, smtp_host: str = None, smtp_port: int = None,
                 smtp_user: str = None, smtp_password: str = None):
        self.smtp_host = smtp_host or "smtp.gmail.com"
        self.smtp_port = smtp_port or 587
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.enabled = bool(smtp_user and smtp_password)
        self.alerts_file = Path("weather_alerts.json")
        self.alerts = self._load_alerts()
        
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        if not self.enabled:
            logger.warning("Email notifications are not configured")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
            
    def send_weather_alert(self, email: str, weather_data: Dict[str, Any]) -> bool:
        subject = f"날씨 알림 - {weather_data.get('city', 'Unknown')}"
        
        body = self._format_weather_alert(weather_data)
        
        return self.send_email(email, subject, body)
        
    def add_alert(self, alert_id: str, email: str, city: str,
                  condition: str, threshold: Any) -> None:
        alert = {
            'id': alert_id,
            'email': email,
            'city': city,
            'condition': condition,
            'threshold': threshold,
            'created_at': datetime.now().isoformat(),
            'last_triggered': None,
            'enabled': True
        }
        
        self.alerts[alert_id] = alert
        self._save_alerts()
        logger.info(f"Alert {alert_id} added for {email}")
        
    def remove_alert(self, alert_id: str) -> bool:
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            self._save_alerts()
            logger.info(f"Alert {alert_id} removed")
            return True
        return False
        
    def check_alerts(self, weather_data: Dict[str, Any]) -> List[str]:
        triggered_alerts = []
        city = weather_data.get('city', '').lower()
        
        for alert_id, alert in self.alerts.items():
            if not alert['enabled']:
                continue
                
            if alert['city'].lower() != city:
                continue
                
            if self._should_trigger_alert(alert, weather_data):
                if self._can_trigger_now(alert):
                    triggered_alerts.append(alert_id)
                    self._trigger_alert(alert, weather_data)
                    
        return triggered_alerts
        
    def _should_trigger_alert(self, alert: Dict, weather_data: Dict) -> bool:
        condition = alert['condition']
        threshold = alert['threshold']
        
        if condition == 'temperature_above':
            return weather_data.get('temperature', 0) > threshold
        elif condition == 'temperature_below':
            return weather_data.get('temperature', 999) < threshold
        elif condition == 'rain':
            return weather_data.get('rain', False)
        elif condition == 'snow':
            return weather_data.get('snow', False)
        elif condition == 'wind_speed_above':
            return weather_data.get('wind_speed', 0) > threshold
        elif condition == 'humidity_above':
            return weather_data.get('humidity', 0) > threshold
        elif condition == 'uv_index_above':
            return weather_data.get('uv_index', 0) > threshold
            
        return False
        
    def _can_trigger_now(self, alert: Dict) -> bool:
        if not alert['last_triggered']:
            return True
            
        last_triggered = datetime.fromisoformat(alert['last_triggered'])
        cooldown_period = timedelta(hours=6)
        
        return datetime.now() - last_triggered > cooldown_period
        
    def _trigger_alert(self, alert: Dict, weather_data: Dict) -> None:
        email_sent = self.send_weather_alert(alert['email'], weather_data)
        
        if email_sent:
            alert['last_triggered'] = datetime.now().isoformat()
            self._save_alerts()
            logger.info(f"Alert {alert['id']} triggered for {alert['email']}")
            
    def _format_weather_alert(self, weather_data: Dict[str, Any]) -> str:
        lines = [
            "날씨 알림",
            "=" * 40,
            f"도시: {weather_data.get('city', 'Unknown')}",
            f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "현재 날씨:",
            f"  온도: {weather_data.get('temperature', 'N/A')}°C",
            f"  체감온도: {weather_data.get('feels_like', 'N/A')}°C",
            f"  습도: {weather_data.get('humidity', 'N/A')}%",
            f"  풍속: {weather_data.get('wind_speed', 'N/A')} m/s",
            f"  날씨: {weather_data.get('description', 'N/A')}",
        ]
        
        if weather_data.get('rain'):
            lines.append(f"  강수량: {weather_data.get('rain_volume', 0)} mm")
            
        if weather_data.get('snow'):
            lines.append(f"  적설량: {weather_data.get('snow_volume', 0)} mm")
            
        return "\n".join(lines)
        
    def _load_alerts(self) -> Dict[str, Dict]:
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load alerts: {e}")
                
        return {}
        
    def _save_alerts(self) -> None:
        try:
            with open(self.alerts_file, 'w') as f:
                json.dump(self.alerts, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")
            
    def get_user_alerts(self, email: str) -> List[Dict]:
        user_alerts = []
        for alert in self.alerts.values():
            if alert['email'] == email:
                user_alerts.append(alert)
        return user_alerts
        
    def toggle_alert(self, alert_id: str) -> bool:
        if alert_id in self.alerts:
            self.alerts[alert_id]['enabled'] = not self.alerts[alert_id]['enabled']
            self._save_alerts()
            return True
        return False