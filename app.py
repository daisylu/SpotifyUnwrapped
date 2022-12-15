# external libraries
import os
from flask import Flask, render_template, redirect, request, session, make_response, session, redirect
import requests
import spotipy
import spotipy.util as util
import base64

# internal modules
from spotify_unwrapped.lyrics import GeniusLyrics
from spotify_unwrapped.top_tracks import TopTracksInfo

app = Flask(__name__)
app.secret_key = os.environ["SPOTIFY_CLIENT_SECRET"]

# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/lyrics", methods=["GET", "POST"])
# def generate_lyrics():
#     if request.method == "POST":
#         # user submitted from site
#         inputs = {k: v for k, v in request.form.items()}

#         # get lyrics
#         g = GeniusLyrics(token = os.environ["GENIUS_CLIENT_ACCESS_TOKEN"])
#         output = g.get_song_lyrics(**inputs)

#         print(output)

#     else:
#         output = "" 

#     return render_template("lyrics.html", output = output)
    
API_BASE = 'https://accounts.spotify.com'
REDIRECT_URI = os.environ["SPOTIFY_REDIRECT_URL"]
SCOPE = 'user-top-read'
CLI_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLI_SEC = os.environ["SPOTIFY_CLIENT_SECRET"]

@app.route("/")
def verify():
    auth_url = f"{API_BASE}/authorize?client_id={CLI_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}&show_dialog=TRUE"
    return redirect(auth_url)

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/callback")
def callback():
    session.clear()
    
    code = request.args.get("code")
    auth_token_url = f"{API_BASE}/api/token"
    
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(code),
        "redirect_uri": REDIRECT_URI
    }
    
    auth = f"{CLI_ID}:{CLI_SEC}"
    base64encoded = base64.urlsafe_b64encode(auth.encode("UTF-8")).decode("ascii")
    headers = {"Authorization": f"Basic {base64encoded}"}
    
    res = requests.post(auth_token_url, data = code_payload, headers = headers)
    res_body = res.json()

    session["token"] = res_body.get("access_token")

    return redirect("index")


@app.route("/go", methods=["POST"])
def go():
    t = TopTracksInfo(session["token"], request.form)
    results_html = t.get_top_tracks_info()
    
    return render_template("results.html", data=request.form, output=results_html)

if __name__ == "__main__":
    app.run(debug=True)