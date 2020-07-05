import os
import pandas as pd
import json
import spotipy
from spotipy import util
import concurrent.futures
import matplotlib

class TopTracksInfo:
    def __init__(self, token, inputs):
        self.sp = spotipy.Spotify(auth = token)
        self.inputs = inputs
        
    @property
    def pitch_class(self):
        return {0: "C",
             1: "C♯, D♭",	
             2: "D",
             3: "D♯, E♭", 
             4: "E",
             5: "F",
             6: "F♯, G♭",
             7: "G",
             8: "G♯, A♭",	
             9: "A",
            10: "A♯, B♭",
            "t": "A♯, B♭",
            "A": "A♯, B♭",
            11: "B",
            "e": "B",
            "B": "B"}
    
    @property
    def track_mode(self):
        return {1: "Major", 0: "Minor"}
    
    def get_top_tracks(self):
        # return df of top tracks
        response = self.sp.current_user_top_tracks(**self.inputs)
        df = pd.DataFrame(response["items"])
        
        # parse nested dictionaries/lists
        df["artists"] = df["artists"].map(lambda x: ", ".join([artist["name"] for artist in x]) if len(x) > 1 else x[0]["name"])
        df["Release Date"] = df["album"].map(lambda x: x["release_date"])
        df["Album Art"] = df["album"].map(lambda x: '<img src="' + x["images"][-1]["url"] + '">')
        df["Album Name"] = df["album"].map(lambda x: x["name"])
        df.rename(columns = {"name": "Track", "popularity": "Track Popularity"}, inplace = True)
        
        self.top_tracks = df
    
    def get_audio_features(self):
        spotify_uri_list = list(self.top_tracks["uri"].values)
        track_audio_features = self.sp.audio_features(spotify_uri_list)
        
        self.track_audio_features = pd.DataFrame(track_audio_features)
        
        # map human-readable names
        self.track_audio_features["key"] = self.track_audio_features["key"].map(lambda x: self.pitch_class[x])
        self.track_audio_features["mode"] = self.track_audio_features["mode"].map(lambda x: self.track_mode[x])
        
    def create_final_df(self):
        # combine top tracks and audio features
        df = self.top_tracks.merge(self.track_audio_features, on = "uri", how = "left")
        df.columns = [c.title() for c in df.columns]
        
        # combined columns to keep
        self.top_track_cols = ["Release Date", "Album Art", "Album Name", "Artists", "Track", "Track Popularity"]
        self.audio_feature_cols = ['Danceability', 'Energy', 'Key', 'Loudness', 'Mode', 'Speechiness', 'Acousticness', 'Instrumentalness', 'Liveness', 'Valence', 'Tempo']
        
        self.results = df[self.top_track_cols + self.audio_feature_cols]
        
    def convert_df_to_html(self):
        audio_feature_formatting = {k: "{:.2}" for k in self.audio_feature_cols if self.results[k].dtype == "float64"}
        audio_feature_formatting.update({"Tempo": lambda x: int(x)})
        
        self.results_html = self.results.style\
            .hide_index()\
            .format(audio_feature_formatting)\
            .background_gradient(cmap="Blues", subset=[c for c in self.audio_feature_cols if self.results[c].dtypes != "object"])\
            .render()
        
    def get_top_tracks_info(self):
        self.get_top_tracks()
        self.get_audio_features()
        self.create_final_df()
        self.convert_df_to_html()
        return self.results_html
        
if __name__ == '__main__':
    pass