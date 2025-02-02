import requests

class SoundchartsClient:
    BASE_URL = "https://customer.api.soundcharts.com/api/v2"

    def __init__(self, app_id, api_key):
        self.headers = {
            "x-app-id": app_id,
            "x-api-key": api_key
        }

    def get_song_metadata(self, song_uuid):
        url = f"{self.BASE_URL}/song/{song_uuid}/metadata"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def get_playlist_metadata(self, playlist_uuid):
        url = f"{self.BASE_URL}/playlist/{playlist_uuid}/metadata"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None 