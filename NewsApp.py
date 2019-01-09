import datetime
import feedparser
import json
import urllib.parse
import urllib.request
from flask import Flask
from flask import make_response
from flask import render_template
from flask import request

app = Flask(__name__)
RSS_FEED = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
            'cnn': 'http://rss.cnn.com/rss/edition.rss',
            'fox': 'http://feeds.foxnews.com/foxnews/latest',
            'iol': 'http://www.iol.co.za/cmlink/1.640'}
DEFAULTS = {'publication': 'bbc',
            'city': 'London,UK',
            'currency_from': 'GBP',
            'currency_to': 'USD'}
weather_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=ac4df081008585814a91c16896e0e40c'
currency_url = 'https://openexchangerates.org//api/latest.json?app_id=a54ac393e8a44df2afb8532e04a5aa96'


@app.route('/')
def home():
    publication = get_value_with_fallback('publication')
    article = get_news(publication)

    # get customized weather based on user inputs or defaults
    city = get_value_with_fallback('city')
    weather = get_weather(city)

    # get customized currencies based on user input

    currency_from = get_value_with_fallback('currency_from')
    currency_to = get_value_with_fallback('currency_to')
    rate, currencies = get_rate(currency_from, currency_to)
    response = make_response(render_template('home.html', article=article, weather=weather, currency_from=currency_from,
                                             currency_to=currency_to, rate=rate,
                                             currencies=sorted(
                                                 currencies)))  # sorted currency to add all currencies to the list

    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response


def get_news(query):
    if not query or query.lower() not in RSS_FEED:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEED[publication])
    return feed['entries']


def get_weather(query):
    query = urllib.parse.quote(query)
    url = weather_url.format(query)
    data = urllib.request.urlopen(url).read()  # load data over HTTP to a python string
    parsed = json.loads(data)  # converts json data to a python dictionary
    weather = None
    if parsed.get('weather'):
        weather = {'description': parsed['weather'][0]['description'],
                   'temperature': parsed['main']['temp'],
                   'city': parsed['name'],
                   'country': parsed['sys']['country']  # sys is country code
                   }
    return weather


def get_rate(frm, to):
    all_currency = urllib.request.urlopen(currency_url).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rates = parsed.get(frm.upper())
    to_rates = parsed.get(to.upper())
    return to_rates / frm_rates, parsed.keys()


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
