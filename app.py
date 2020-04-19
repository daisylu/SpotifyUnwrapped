from lyrics import get_song_lyrics
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
#     return "hello world"
    title = get_song_lyrics("I can't believe I had you", "Emmit Fenn")
    return title

if __name__ == '__main__':
    app.run()