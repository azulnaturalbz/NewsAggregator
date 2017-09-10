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

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication': 'bbc',
            'city': 'Belize,bz',
            'currency_from': 'BZD',
            'currency_to': 'USD'}

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=f47aeab3995ca500141e77a82f634ba6"
CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=3939e9bcc6ab47719d6da46537c431e6"


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


@app.route("/")
def home():
    # get cust headlines , based on user input or default
    publication = request.args.get("publication")
    if not publication:
        publication = request.cookies.get("publication")
        if not publication:
            publication = DEFAULTS['publication']
    articles = get_news(publication)
    # get cust weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    # get customized currency from user input or default
    currency_from = request.args.get("currency_from")
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
    currency_to = request.args.get("currency_to")
    if not currency_to:
        currency_to = DEFAULTS['currency_to']
    rate, currencies = get_rate(currency_from, currency_to)
    #return render_template("home.html", articles=articles, weather=weather, currency_from=currency_from,currency_to=currency_to, rate=rate, currencies=sorted(currencies))
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


#Version 1
# import feedparser
# from flask import Flask
#
# app = Flask(__name__)
#
#
# BBC_FEED = "http://feeds.bbci.co.uk/news/rss.xml"
#
# @app.route('/')
# def get_news():
#     feed = feedparser.parse(BBC_FEED)
#     first_article = feed['entries'][0]
#     return """
#     <html>
#     <body>
#     <h1>BBC Headlines</h1>
#     <b>{0}</b><br/>
#     <i>{1}</i><br/>
#     <p>{2}</p><br/>
#     </body>
#     <html>
#     """.format(first_article.get("title"),first_article.get("published"),first_article.get("summary"))
#
# if __name__ == '__main__':
#     app.run()

# Version2
# @app.route("/")
# @app.route("/<publication>")
# def get_news(publication="bbc"):
#     feed = feedparser.parse(RSS_FEEDS[publication])
#     first_article=feed['entries'][0]
#     return """
#     <html>
#     <body>
#     <h1>Headlines</h1>
#     <b>{0}</b><br/>
#     <i>{1}</i><br/>
#     <p>{2}</p><br/>
#     </body>
#     </html>
#     """.format(first_article.get("title"),first_article.get("published"),first_article.get("summary"))
