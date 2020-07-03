import os
import requests
from bs4 import BeautifulSoup
import unicodedata

class GeniusLyrics:
    def __init__(self, token):
        self.token = token

    def query_genius(self, song_title, artist_name):
        
        base_url = "https://api.genius.com"
        headers = {"Authorization": "Bearer " + self.token}
        search_url = base_url + "/search"
        data = {"q": song_title + " " + artist_name}

        response = requests.get(search_url, data=data, headers=headers)

        return response

    def parse_genius_response(self, response):

        if response.status_code == 200:
            response = response.json()
            first_hit = response["response"]["hits"][0]["result"]
            full_title = unicodedata.normalize("NFKD", first_hit["full_title"])
            lyrics_url = first_hit["url"]
            
        return full_title, lyrics_url

    def scrap_song_url(self, url):

        page = requests.get(url)

        if page.status_code == 200:
            html = BeautifulSoup(page.text, "html.parser")
            lyrics = html.find("div", class_="lyrics").get_text()
            lyrics = unicodedata.normalize("NFKD", lyrics)
        else:
            lyrics = "Not found."

        return lyrics

    def get_song_lyrics(self, song_title, artist_name):
        
        response = self.query_genius(song_title, artist_name)
        title, url = self.parse_genius_response(response)
        lyrics_text = self.scrap_song_url(url)
        
        return lyrics_text