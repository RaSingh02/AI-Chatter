import requests
import logging
import os
import sys
from pathlib import Path

# Add the root directory to the system path
sys.path.append(str(Path(__file__).parent.parent))

from config.config import Config
from utils.utils import setup_logging

setup_logging()

class TwitchAPI:
    """Base class for Twitch API interactions"""
    
    def __init__(self, client_id=None, access_token=None):
        """Initialize the Twitch API handler"""
        self.client_id = client_id or Config.TWITCH_CLIENT_ID
        self.access_token = access_token or Config.TWITCH_ACCESS_TOKEN
        self.refresh_token = Config.TWITCH_REFRESH_TOKEN
        self.base_url = "https://api.twitch.tv/helix"
        
        if not self.client_id or not self.access_token:
            logging.error("Missing Twitch credentials. Check your .env file.")
            raise ValueError("Twitch API credentials not found")
        
        self.session = requests.Session()
        self.headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }
    
    def get_user_by_login(self, username):
        """Get user details by username"""
        url = f"{self.base_url}/users"
        params = {"login": username}
        
        try:
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            if data and data.get("data") and len(data["data"]) > 0:
                return data["data"][0]
            return None
        except requests.RequestException as e:
            logging.error(f"Error getting user info: {e}")
            return None
    
    def get_stream(self, user_id=None, username=None):
        """Check if a stream is live using user_id or username"""
        url = f"{self.base_url}/streams"
        params = {}
        
        if user_id:
            params["user_id"] = user_id
        elif username:
            params["user_login"] = username
        else:
            raise ValueError("Either user_id or username must be provided")
        
        try:
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            if data and data.get("data") and len(data["data"]) > 0:
                return data["data"][0]  # Stream is live
            return None  # Stream is offline
        except requests.RequestException as e:
            logging.error(f"Error checking stream status: {e}")
            return None
    
    def refresh_auth_token(self):
        """Refresh the authentication token"""
        if not self.refresh_token:
            logging.error("No refresh token available")
            return False
        
        url = "https://id.twitch.tv/oauth2/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": os.getenv("CLIENT_SECRET", ""),
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            data = response.json()
            
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            self.headers["Authorization"] = f"Bearer {self.access_token}"
            
            logging.info("Successfully refreshed authentication token")
            return True
        except requests.RequestException as e:
            logging.error(f"Error refreshing token: {e}")
            return False
