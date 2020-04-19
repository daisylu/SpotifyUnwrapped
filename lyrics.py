import os
import requests
from bs4 import BeautifulSoup
import unicodedata

def parse_genius_response(response):
    if response["meta"]["status"] == 200:
        first_hit = response["response"]["hits"][0]["result"]
        full_title = unicodedata.normalize("NFKD", first_hit["full_title"])
        lyrics_url = first_hit["url"]
    return full_title, lyrics_url

def query_genius(song_title, artist_name):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + os.environ["GENIUS_CLIENT_ACCESS_TOKEN"]}
    search_url = base_url + '/search'
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(search_url, data=data, headers=headers)
    return response.json()

def scrap_song_url(url):
    print(url)
    page = requests.get(url)
    print(page.status)
    html = BeautifulSoup(page.text, "html.parser")
    lyrics = html.find("div", class_="lyrics").get_text()
    print(lyrics)
    lyrics = unicodedata.normalize("NFKD", lyrics)
    return lyrics

def get_song_lyrics(song_title, artist_name):
    response = query_genius(song_title, artist_name)
    title, url = parse_genius_response(response)
    lyrics_text = scrap_song_url(url)
    return title, lyrics_text