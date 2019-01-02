import feedparser
import json
import urllib.parse
import urllib.request
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)
RSS_FEED = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
            'cnn': 'http://rss.cnn.com/rss/edition.rss',
            'fox': 'http://feeds.foxnews.com/foxnews/latest',
            'iol': 'http://www.iol.co.za/cmlink/1.640'}
DEFAULTS = {'publication': 'bbc',
            'city': 'London,UK'}


@app.route('/')
def home():
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    article = get_news(publication)

    # get customized weather based on user inputs or defaults
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    return render_template('home.html', article=article, weather=weather)


def get_news(query):
    if not query or query.lower() not in RSS_FEED:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEED[publication])
    return feed['entries']


def get_weather(query):
    api_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=ac4df081008585814a91c16896e0e40c'
    query = urllib.parse.quote(query)
    url = api_url.format(query)
    data = urllib.request.urlopen(url).read()  # load data over HTTP to a python string
    parsed = json.loads(data)  # converts json data to a python dictionary
    weather = None
    if parsed.get('weather'):
        weather = {'description': parsed['weather'][0]['description'],
                   'temperature': parsed['main']['temp'],
                   'city': parsed['name'],
                   'country': parsed['sys']['country']  #sys is country code
                   }
    return weather


if __name__ == '__main__':
    app.run(port=5000, debug=True)
