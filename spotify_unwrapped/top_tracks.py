import os
import pandas as pd
import json
import spotipy
from spotipy import util
import concurrent.futures
import matplotlib
from IPython.core.display import HTML

class TopTracksInfo:
    def __init__(self, token, inputs):
        self.sp = spotipy.Spotify(auth = token)
        self.inputs = inputs
    
    def get_top_tracks(self):
        # return df of top tracks
        response = self.sp.current_user_top_tracks(**self.inputs)
        df = pd.DataFrame(response["items"])
        
        # parse nested dictionaries/lists
        df["Artist(s)"] = df["artists"].map(lambda x: ", ".join([artist["name"] for artist in x]) if len(x) > 1 else x[0]["name"])
        df["Release Date"] = df["album"].map(lambda x: x["release_date"])
        df["Album Art"] = df["album"].map(lambda x: '<img src="' + x["images"][-1]["url"] + '">')
        df["Album Name"] = df["album"].map(lambda x: x["name"])
        df.rename(columns = {"name": "Track", "popularity": "User Popularity"}, inplace = True)
        
        self.top_tracks = df
    
    def get_audio_features(self):
        # threads used = total number of tracks
        threads = int(self.inputs["limit"])
        
        # audio_features method takes spotify URIs as arguments
        spotify_uri_list = self.top_tracks["uri"].values
        
        # multithread call
        with concurrent.futures.ThreadPoolExecutor(max_workers = threads) as executor:
            results = executor.map(self.sp.audio_features, spotify_uri_list)

        # return results in df
        track_audio_features = [track[0] for track in list(results)]
        self.track_audio_features = pd.DataFrame(track_audio_features)
        
    def create_final_df(self):
        df = self.top_tracks.merge(self.track_audio_features, on = "uri", how = "left")
        
        # combined columns to keep
        top_track_cols = ["Release Date", "Album Art", "Album Name", "Artist(s)", "Track", "User Popularity"]
        audio_feature_cols = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
        
        self.results = df[top_track_cols + audio_feature_cols]
        
    def convert_df_to_html(self):
        self.results_html = self.results.style.background_gradient(cmap="Blues").render()
#         results_html = HTML(self.results.to_html(escape=False))
        
    def get_top_tracks_info(self):
        self.get_top_tracks()
        self.get_audio_features()
        self.create_final_df()
        self.convert_df_to_html()
        return self.results_html
        
if __name__ == '__main__':
    pass