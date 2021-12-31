import json
from urllib.request import urlopen
from urllib.parse import quote
import feedparser
import datetime
from flask import make_response
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

RSS_FEEDS = {'breaking-belize-news': 'https://www.breakingbelizenews.com/feed/',
             'love-news': 'http://lovefm.com/feed/',
             'amandala': 'http://amandala.com.bz/news/feed/',
             'san-pedro-sun': 'https://www.sanpedrosun.com/feed/',
             'reporter': 'http://www.reporter.bz/feed/',
             'mybelize': 'http://www.mybelize.net/feed/'}

DEFAULTS = {'publication': 'breaking-belize-news',
            'city': 'Belize,bz',
            'currency_from': 'BZD',
            'currency_to': 'USD'}

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=1f3d91f00155c1f35b07c2237891ded0"


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


@app.route("/")
def home():
    # get cust headlines , based on user input or default
    publication = get_value_with_fallback("publication")
    articles = get_news(publication)
# get cust weather based on user input or default
    city = get_value_with_fallback("city")
    weather = get_weather(city)
# get customized currency from user input or default
    response = make_response(render_template(
        "home.html", articles=articles, weather=weather, options=RSS_FEEDS))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    return response


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(query):
    query = quote(query)
    url = WEATHER_URL.format(query)
    data = urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"],
                   "temperature": parsed["main"]["temp"],
                   "city": parsed["name"],
                   "country": parsed['sys']['country']}
    return weather


if __name__ == '__main__':
    app.run()
