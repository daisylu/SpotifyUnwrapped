import os
import pandas as pd
import json
import spotipy
from spotipy import util
import concurrent.futures

class TopTracksInfo:
    def __init__(self, token, inputs):
        self.token = token
        self.inputs = inputs
    
    def call_spotipy(self):
        self.sp = spotipy.Spotify(auth = self.token)
        self.response = self.sp.current_user_top_tracks(**self.inputs)
    
    def parse_top_tracks(self):
        df = pd.DataFrame(self.response["items"])
        
        # parse nested dictionaries/lists
        df["Artists"] = df["artists"].map(lambda x: [artist["name"] for artist in x])
        df["Release Date"] = df["album"].map(lambda x: x["release_date"])
        df["Album"] = df["album"].map(lambda x: x["name"])
        df.rename(columns = {"name": "Track", "popularity": "User Popularity"}, inplace = True)
        
        self.top_tracks = df
    
    def multithread_audio_features_call(self):
        threads = int(self.inputs["limit"])
        
        spotify_uri_list = self.top_tracks["uri"].values
        
        with concurrent.futures.ThreadPoolExecutor(max_workers = threads) as executor:
            results = executor.map(self.sp.audio_features, spotify_uri_list)

        track_audio_features = [track[0] for track in list(results)]
        self.track_audio_features = pd.DataFrame(track_audio_features)
        
    def create_final_df(self):
        df = self.top_tracks.merge(self.track_audio_features, on = "uri", how = "left")
        
        top_track_cols = ["Release Date", "Album", "Artists", "Track", "User Popularity"]
        audio_feature_cols = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
        
        self.results = df[top_track_cols + audio_feature_cols]
        
    def get_top_tracks_info(self):
        self.call_spotipy()
        self.parse_top_tracks()
        self.multithread_audio_features_call()
        self.create_final_df()
        return self.results
        
if __name__ == '__main__':
    pass