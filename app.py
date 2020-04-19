from lyrics import get_song_lyrics
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
#     return "hello world"
    title, lyrics = get_song_lyrics("I can't believe I had you", "Emmit Fenn")
    return title, lyrics

if __name__ == '__main__':
    app.run()