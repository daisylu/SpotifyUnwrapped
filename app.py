import os
from dotenv import load_dotenv
from flask import Flask, request, render_template

from spotify_unwrapped.lyrics import GeniusLyrics

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/lyrics", methods=["GET", "POST"])
def generate_lyrics():
    if request.method == "POST":
        # user submitted from site
        inputs = {k: v for k, v in request.form.items()}
        print(inputs)

        # get lyrics
        g = GeniusLyrics(token = os.environ["GENIUS_CLIENT_ACCESS_TOKEN"])
        output = g.get_song_lyrics(**inputs)

    else:
        output = "" 

    return render_template("index.html", output = output)

if __name__ == "__main__":
    load_dotenv()

    app.run(debug=True)