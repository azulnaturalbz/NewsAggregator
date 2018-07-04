import json
import urllib2
import urllib
import feedparser
import datetime
from flask import make_response
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

RSS_FEEDS = {'bbn': 'https://www.breakingbelizenews.com/feed/',
             'lov': 'http://lovefm.com/feed/',
             'amd': 'http://amandala.com.bz/news/feed/',
             'sps': 'https://www.sanpedrosun.com/feed/',
             'rpt': 'http://www.reporter.bz/feed/',
             'mybz':'http://www.mybelize.net/feed/'}

DEFAULTS = {'publication': 'bbn',
            'city': 'Belize,bz',
            'currency_from': 'BZD',
            'currency_to': 'USD'}

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=addyourownappid"
CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=addyourownappid"


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
    articles=get_news(publication)
# get cust weather based on user input or default
    city = get_value_with_fallback("city")
    weather = get_weather(city)
# get customized currency from user input or default
    currency_from = get_value_with_fallback("currency_from")
    currency_to = get_value_with_fallback("currency_to")
    rate, currencies = get_rate(currency_from, currency_to)
    response = make_response(render_template("home.html", articles=articles, weather=weather, currency_from=currency_from,currency_to=currency_to, rate=rate, currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication",publication,expires=expires)
    response.set_cookie("city",city,expires=expires)
    response.set_cookie("currency_from",currency_from,expires=expires)
    response.set_cookie("currency_to",currency_to,expires=expires)
    return response

  
def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(query):
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=f47aeab3995ca500141e77a82f634ba6"
    query = urllib.quote(query)
    url = api_url.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"],
                   "temperature": parsed["main"]["temp"],
                   "city": parsed["name"],
                   "country": parsed['sys']['country']}
    return weather


def get_rate(frm, to):
    all_currency = urllib2.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return to_rate / frm_rate, parsed.keys()


if __name__ == '__main__':
    app.run()
